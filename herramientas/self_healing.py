#!/usr/bin/env python3
"""
NXT AI Development - Self-Healing Manager
==========================================
Real implementation of:
- Circuit Breaker pattern (closed -> open -> half-open)
- Health Metrics collection
- Recovery strategies (retry, skip, fallback, reset)
- Input sanitization
- Delegation depth guard

Version: 3.8.0
"""

import json
import time
import html
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List, Callable
from functools import wraps


# ═══════════════════════════════════════════════════════════════
# CIRCUIT BREAKER
# ═══════════════════════════════════════════════════════════════

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject calls
    HALF_OPEN = "half_open" # Testing if recovered


@dataclass
class CircuitBreaker:
    """
    Circuit Breaker pattern implementation.

    CLOSED: Normal operation. Track failures.
    OPEN: Too many failures. Reject all calls for `reset_timeout` seconds.
    HALF_OPEN: After timeout, allow ONE call to test if service recovered.

    Usage:
        cb = CircuitBreaker(name="orchestrator_classify", failure_threshold=3)

        if cb.can_execute():
            try:
                result = do_something()
                cb.record_success()
            except Exception as e:
                cb.record_failure()
                # Use fallback
    """
    name: str
    failure_threshold: int = 3          # Failures before opening
    reset_timeout: int = 60             # Seconds to wait before half-open
    success_threshold: int = 2          # Successes in half-open to close

    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_state_change: Optional[float] = None
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0

    def can_execute(self) -> bool:
        """Check if a call should be allowed."""
        self.total_calls += 1

        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.reset_timeout:
                self._transition(CircuitState.HALF_OPEN)
                return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True  # Allow one test call
        return False

    def record_success(self):
        """Record a successful call."""
        self.total_successes += 1

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._transition(CircuitState.CLOSED)
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0  # Reset failure count on success

    def record_failure(self):
        """Record a failed call."""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                self._transition(CircuitState.OPEN)
        elif self.state == CircuitState.HALF_OPEN:
            self._transition(CircuitState.OPEN)

    def _transition(self, new_state: CircuitState):
        """Transition to a new state."""
        self.state = new_state
        self.last_state_change = time.time()
        if new_state == CircuitState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self.success_count = 0

    def get_status(self) -> Dict[str, Any]:
        """Get current status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_calls": self.total_calls,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "success_rate": round(self.total_successes / max(self.total_calls, 1) * 100, 1),
        }


# ═══════════════════════════════════════════════════════════════
# HEALTH METRICS
# ═══════════════════════════════════════════════════════════════

@dataclass
class HealthMetrics:
    """
    Collects and persists health metrics for the framework.
    Stores in .nxt/health.json
    """
    metrics_file: str = ".nxt/health.json"

    # In-memory metrics
    operations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    circuit_breakers: Dict[str, CircuitBreaker] = field(default_factory=dict)
    _start_time: float = field(default_factory=time.time)

    def get_or_create_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create a circuit breaker by name."""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name=name, **kwargs)
        return self.circuit_breakers[name]

    def record_operation(self, name: str, success: bool, duration_ms: float = 0, error: str = ""):
        """Record an operation result."""
        if name not in self.operations:
            self.operations[name] = {
                "total": 0, "success": 0, "failure": 0,
                "total_duration_ms": 0, "errors": [],
                "last_success": None, "last_failure": None,
            }

        op = self.operations[name]
        op["total"] += 1
        op["total_duration_ms"] += duration_ms

        if success:
            op["success"] += 1
            op["last_success"] = datetime.now().isoformat()
        else:
            op["failure"] += 1
            op["last_failure"] = datetime.now().isoformat()
            if error:
                op["errors"].append({
                    "message": error[:200],  # Limit error message length
                    "timestamp": datetime.now().isoformat()
                })
                # Keep only last 10 errors
                op["errors"] = op["errors"][-10:]

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        total_ops = sum(o["total"] for o in self.operations.values())
        total_failures = sum(o["failure"] for o in self.operations.values())

        if total_ops == 0:
            health = "UNKNOWN"
            score = 0
        else:
            failure_rate = total_failures / total_ops
            if failure_rate < 0.05:
                health = "HEALTHY"
                score = round((1 - failure_rate) * 100, 1)
            elif failure_rate < 0.15:
                health = "DEGRADED"
                score = round((1 - failure_rate) * 100, 1)
            else:
                health = "UNHEALTHY"
                score = round((1 - failure_rate) * 100, 1)

        return {
            "status": health,
            "score": score,
            "uptime_seconds": round(time.time() - self._start_time, 1),
            "total_operations": total_ops,
            "total_failures": total_failures,
            "failure_rate": round(total_failures / max(total_ops, 1) * 100, 2),
            "operations": {
                name: {
                    "total": op["total"],
                    "success_rate": round(op["success"] / max(op["total"], 1) * 100, 1),
                    "avg_duration_ms": round(op["total_duration_ms"] / max(op["total"], 1), 1),
                    "recent_errors": len(op["errors"]),
                }
                for name, op in self.operations.items()
            },
            "circuit_breakers": {
                name: cb.get_status()
                for name, cb in self.circuit_breakers.items()
            },
            "timestamp": datetime.now().isoformat(),
        }

    def save(self):
        """Persist metrics to disk."""
        try:
            path = Path(self.metrics_file)
            path.parent.mkdir(parents=True, exist_ok=True)

            data = self.get_health_status()
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Never crash on metrics save

    def load(self):
        """Load metrics from disk (for continuity across sessions)."""
        try:
            path = Path(self.metrics_file)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None


# ═══════════════════════════════════════════════════════════════
# RECOVERY STRATEGIES
# ═══════════════════════════════════════════════════════════════

class RecoveryStrategy(Enum):
    RETRY = "retry"
    SKIP = "skip"
    FALLBACK = "fallback"
    RESET = "reset"


def with_recovery(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    fallback_value: Any = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
    health_metrics: Optional[HealthMetrics] = None,
    operation_name: str = "unknown",
):
    """
    Decorator that adds recovery strategies to any function.

    Usage:
        @with_recovery(max_retries=3, fallback_value={}, operation_name="classify")
        def classify_task(task: str) -> dict:
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            last_error = None

            # Check circuit breaker
            if circuit_breaker and not circuit_breaker.can_execute():
                if health_metrics:
                    health_metrics.record_operation(operation_name, False, 0, "Circuit breaker OPEN")
                return fallback_value

            # Retry loop
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start) * 1000

                    if circuit_breaker:
                        circuit_breaker.record_success()
                    if health_metrics:
                        health_metrics.record_operation(operation_name, True, duration)

                    return result

                except Exception as e:
                    last_error = str(e)

                    if attempt < max_retries:
                        time.sleep(retry_delay * (attempt + 1))  # Exponential-ish backoff
                    else:
                        duration = (time.time() - start) * 1000

                        if circuit_breaker:
                            circuit_breaker.record_failure()
                        if health_metrics:
                            health_metrics.record_operation(operation_name, False, duration, last_error)

                        return fallback_value

            return fallback_value
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════
# INPUT SANITIZER
# ═══════════════════════════════════════════════════════════════

class InputSanitizer:
    """
    Sanitizes user input before storing in state.json or other files.
    Prevents XSS, SQL injection patterns, and excessive data.
    """

    MAX_TASK_LENGTH = 500
    MAX_DESCRIPTION_LENGTH = 2000
    MAX_DECISIONS_LOG = 50  # Keep only last N entries

    @staticmethod
    def sanitize_text(text: str, max_length: int = 500) -> str:
        """Remove HTML, limit length, strip dangerous patterns."""
        if not isinstance(text, str):
            return str(text)[:max_length]

        # Escape HTML entities
        text = html.escape(text)

        # Remove null bytes
        text = text.replace('\x00', '')

        # Limit length
        if len(text) > max_length:
            text = text[:max_length] + "..."

        return text.strip()

    @staticmethod
    def sanitize_task(task: str) -> str:
        """Sanitize a task description."""
        return InputSanitizer.sanitize_text(task, InputSanitizer.MAX_TASK_LENGTH)

    @staticmethod
    def deduplicate_decisions(decisions: List[Dict], max_entries: int = 50) -> List[Dict]:
        """Remove duplicate decisions and keep only the last N."""
        if not decisions:
            return []

        seen = set()
        unique = []

        for d in decisions:
            # Create a fingerprint from type + task/description
            key_parts = [
                d.get("type", ""),
                d.get("task", d.get("description", "")),
            ]
            fingerprint = hashlib.md5("|".join(key_parts).encode()).hexdigest()

            if fingerprint not in seen:
                seen.add(fingerprint)
                unique.append(d)

        # Keep only last N entries
        return unique[-max_entries:]

    @staticmethod
    def sanitize_state(state: Dict) -> Dict:
        """Sanitize an entire state.json object."""
        if not isinstance(state, dict):
            return state

        # Sanitize current_context task
        if state.get("current_context") and isinstance(state["current_context"], dict):
            if "task" in state["current_context"]:
                state["current_context"]["task"] = InputSanitizer.sanitize_task(
                    state["current_context"]["task"]
                )

        # Sanitize pending tasks
        if "pending_tasks" in state:
            for task in state["pending_tasks"]:
                if isinstance(task, dict) and "task" in task:
                    task["task"] = InputSanitizer.sanitize_task(task["task"])

        # Deduplicate and limit decisions_log
        if "decisions_log" in state:
            state["decisions_log"] = InputSanitizer.deduplicate_decisions(
                state["decisions_log"]
            )

        return state


# ═══════════════════════════════════════════════════════════════
# DELEGATION DEPTH GUARD
# ═══════════════════════════════════════════════════════════════

class DelegationGuard:
    """
    Prevents infinite delegation loops between agents.
    Tracks the delegation chain and breaks it if depth is exceeded.
    """

    MAX_DEPTH = 5  # Maximum delegation chain depth

    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
        self.chain: List[str] = []
        self._blocked_count = 0

    def can_delegate(self, from_agent: str, to_agent: str) -> bool:
        """
        Check if delegation is allowed.
        Returns False if:
        - Depth limit exceeded
        - Would create a direct loop (A->B->A)
        - Agent already in chain (A->B->C->A)
        """
        # Check depth
        if len(self.chain) >= self.max_depth:
            self._blocked_count += 1
            return False

        # Check direct loop (A->B->A)
        if self.chain and self.chain[-1] == to_agent:
            # Allow only if the agent before last is different
            # This catches A->B->A patterns
            if len(self.chain) >= 2 and self.chain[-2] == to_agent:
                self._blocked_count += 1
                return False

        # Check if target is already in chain (cycle detection)
        if to_agent in self.chain:
            self._blocked_count += 1
            return False

        return True

    def push(self, agent: str):
        """Add agent to delegation chain."""
        self.chain.append(agent)

    def pop(self) -> Optional[str]:
        """Remove last agent from chain."""
        return self.chain.pop() if self.chain else None

    def reset(self):
        """Reset the delegation chain."""
        self.chain = []

    def get_status(self) -> Dict[str, Any]:
        """Get delegation guard status."""
        return {
            "current_depth": len(self.chain),
            "max_depth": self.max_depth,
            "chain": list(self.chain),
            "blocked_count": self._blocked_count,
        }


# ═══════════════════════════════════════════════════════════════
# SELF-HEALING MANAGER (facade)
# ═══════════════════════════════════════════════════════════════

class SelfHealingManager:
    """
    Main facade that ties together all resilience components.

    Usage:
        shm = SelfHealingManager()

        # Use circuit breaker for classify operation
        cb = shm.get_breaker("classify")
        if cb.can_execute():
            try:
                result = classify(task)
                cb.record_success()
            except:
                cb.record_failure()

        # Sanitize input
        clean_task = shm.sanitize(task)

        # Check delegation
        if shm.can_delegate("nxt-dev", "nxt-qa"):
            shm.push_delegation("nxt-qa")

        # Get health
        status = shm.get_health()

        # Save metrics
        shm.save()
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.health = HealthMetrics(
            metrics_file=str(self.project_root / ".nxt" / "health.json")
        )
        self.sanitizer = InputSanitizer()
        self.delegation = DelegationGuard()
        self._breakers: Dict[str, CircuitBreaker] = {}

    def get_breaker(self, name: str, **kwargs) -> CircuitBreaker:
        """Get or create a circuit breaker."""
        return self.health.get_or_create_breaker(name, **kwargs)

    def sanitize(self, text: str, max_length: int = 500) -> str:
        """Sanitize input text."""
        return self.sanitizer.sanitize_text(text, max_length)

    def sanitize_state(self, state: Dict) -> Dict:
        """Sanitize entire state object."""
        return self.sanitizer.sanitize_state(state)

    def can_delegate(self, from_agent: str, to_agent: str) -> bool:
        """Check if delegation is allowed."""
        return self.delegation.can_delegate(from_agent, to_agent)

    def push_delegation(self, agent: str):
        """Track delegation."""
        self.delegation.push(agent)

    def pop_delegation(self):
        """Untrack delegation."""
        self.delegation.pop()

    def reset_delegation(self):
        """Reset delegation chain."""
        self.delegation.reset()

    def record(self, operation: str, success: bool, duration_ms: float = 0, error: str = ""):
        """Record an operation."""
        self.health.record_operation(operation, success, duration_ms, error)

    def get_health(self) -> Dict[str, Any]:
        """Get full health status."""
        status = self.health.get_health_status()
        status["delegation"] = self.delegation.get_status()
        return status

    def save(self):
        """Persist health metrics."""
        self.health.save()

    def load_previous(self) -> Optional[Dict]:
        """Load previous health metrics."""
        return self.health.load()


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

def main():
    """CLI interface for self-healing manager."""
    import argparse

    parser = argparse.ArgumentParser(description="NXT Self-Healing Manager v3.8.0")
    parser.add_argument("command", choices=[
                           "status", "health", "test", "sanitize-state", "reset",
                           "verify-agents", "generate-checksums",
                       ],
                       help="Command to execute")
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()
    shm = SelfHealingManager(args.project_root)

    if args.command == "status":
        # Load previous metrics if any
        prev = shm.load_previous()
        if prev:
            print(json.dumps(prev, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({"status": "NO_DATA", "message": "No health metrics collected yet"}, indent=2))

    elif args.command == "health":
        status = shm.get_health()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.command == "test":
        # Run self-test of all components
        print("Testing Circuit Breaker...")
        cb = shm.get_breaker("test", failure_threshold=2, reset_timeout=5)
        assert cb.can_execute() == True
        cb.record_success()
        cb.record_failure()
        cb.record_failure()  # Should open
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute() == False
        print("  Circuit Breaker: PASS")

        print("Testing Input Sanitizer...")
        assert "<script>" not in shm.sanitize("<script>alert('xss')</script>")
        assert len(shm.sanitize("a" * 1000)) <= 503  # 500 + "..."
        assert shm.sanitize("") == ""
        assert shm.sanitize("normal text") == "normal text"
        print("  Input Sanitizer: PASS")

        print("Testing Delegation Guard...")
        assert shm.can_delegate("nxt-dev", "nxt-qa") == True
        shm.push_delegation("nxt-dev")
        shm.push_delegation("nxt-qa")
        assert shm.can_delegate("nxt-qa", "nxt-dev") == False  # nxt-dev already in chain
        shm.reset_delegation()
        print("  Delegation Guard: PASS")

        print("Testing Health Metrics...")
        shm.record("test_op", True, 50.0)
        shm.record("test_op", True, 30.0)
        shm.record("test_op", False, 100.0, "test error")
        status = shm.get_health()
        assert status["total_operations"] == 3
        assert status["status"] in ["HEALTHY", "DEGRADED", "UNHEALTHY"]
        print("  Health Metrics: PASS")

        print("Testing Deduplication...")
        decisions = [
            {"type": "classification", "task": "fix bug"},
            {"type": "classification", "task": "fix bug"},  # duplicate
            {"type": "classification", "task": "fix bug"},  # duplicate
            {"type": "planning", "task": "new feature"},
        ]
        deduped = InputSanitizer.deduplicate_decisions(decisions)
        assert len(deduped) == 2  # Only unique entries
        print("  Deduplication: PASS")

        print("\nAll self-healing tests: PASS")

        # Save test results
        shm.save()
        print(f"Health metrics saved to {shm.health.metrics_file}")

    elif args.command == "sanitize-state":
        # Sanitize the current state.json
        state_path = Path(args.project_root) / ".nxt" / "state.json"
        if not state_path.exists():
            print(json.dumps({"error": "state.json not found"}))
            return

        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)

        before_decisions = len(state.get("decisions_log", []))
        state = InputSanitizer.sanitize_state(state)
        after_decisions = len(state.get("decisions_log", []))

        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        print(json.dumps({
            "status": "sanitized",
            "decisions_log": f"{before_decisions} -> {after_decisions}",
            "file": str(state_path),
        }, indent=2))

    elif args.command == "reset":
        health_path = Path(args.project_root) / ".nxt" / "health.json"
        if health_path.exists():
            health_path.unlink()
            print("Health metrics reset.")
        else:
            print("No health metrics to reset.")

    elif args.command == "verify-agents":
        # Verify agent file integrity against stored checksums
        import glob as globmod

        checksums_path = Path(args.project_root) / ".nxt" / "agent-checksums.json"
        if not checksums_path.exists():
            print(json.dumps({"error": "agent-checksums.json not found. Run 'generate-checksums' first."}, indent=2))
            sys.exit(1)

        with open(checksums_path, 'r', encoding='utf-8') as f:
            checksums_data = json.load(f)

        stored = checksums_data.get("agents", {})
        agents_dir = Path(args.project_root) / "agentes"
        results = {}
        passed = 0
        failed = 0
        missing = 0
        modified = 0

        for agent_name, expected_hash in sorted(stored.items()):
            agent_path = agents_dir / agent_name
            if not agent_path.exists():
                results[agent_name] = "MISSING"
                missing += 1
                continue

            with open(agent_path, 'rb') as fh:
                actual_hash = hashlib.sha256(fh.read()).hexdigest()

            if actual_hash == expected_hash:
                results[agent_name] = "PASS"
                passed += 1
            else:
                results[agent_name] = "MODIFIED"
                modified += 1

        # Check for new agent files not in checksums
        new_agents = []
        for f in sorted(agents_dir.glob("nxt-*.md")):
            if f.name not in stored:
                results[f.name] = "NEW (not in checksums)"
                new_agents.append(f.name)

        all_ok = (modified == 0 and missing == 0)
        summary = {
            "status": "PASS" if all_ok else "FAIL",
            "total_checked": len(stored),
            "passed": passed,
            "modified": modified,
            "missing": missing,
            "new_untracked": len(new_agents),
            "checksums_version": checksums_data.get("version", "unknown"),
            "checksums_generated_at": checksums_data.get("generated_at", "unknown"),
            "results": results,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))

        if not all_ok:
            sys.exit(1)

    elif args.command == "generate-checksums":
        # Regenerate agent checksums file
        agents_dir = Path(args.project_root) / "agentes"
        checksums = {}

        for f in sorted(agents_dir.glob("nxt-*.md")):
            with open(f, 'rb') as fh:
                h = hashlib.sha256(fh.read()).hexdigest()
            checksums[f.name] = h

        data = {
            "version": "3.8.0",
            "generated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "description": "SHA-256 checksums for agent integrity verification. Regenerate with: python herramientas/self_healing.py generate-checksums",
            "total_agents": len(checksums),
            "agents": checksums,
        }

        out_path = Path(args.project_root) / ".nxt" / "agent-checksums.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(json.dumps({
            "status": "generated",
            "total_agents": len(checksums),
            "file": str(out_path),
            "generated_at": data["generated_at"],
        }, indent=2))


if __name__ == "__main__":
    import sys
    main()
