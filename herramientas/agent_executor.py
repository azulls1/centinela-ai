#!/usr/bin/env python3
"""
NXT Agent Executor v3.8.0
=========================
Lightweight agent execution planner for the NXT framework.
Plans and tracks agent execution sequences without external CLI dependencies.

Since v3.4.0, agents execute via Claude reading agent files directly.
This module provides:
- Execution planning (which agents in what order)
- State tracking (progress, artifacts, decisions)
- Dry-run simulation
- Checkpoint integration

Usage:
    python agent_executor.py plan "add auth feature" --agents nxt-dev,nxt-qa
    python agent_executor.py dry-run "add auth feature"
    python agent_executor.py list
    python agent_executor.py status <plan_id>
"""

import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import Enum

# ---------------------------------------------------------------------------
# Optional telemetry import
# ---------------------------------------------------------------------------
try:
    from nxt_telemetry import emit_event as _telemetry_emit
except Exception:
    _telemetry_emit = None

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Agents recommended per scale level (mirrors nxt_orchestrator_v3 LEVEL_CONFIG)
SCALE_AGENTS: Dict[str, List[str]] = {
    "nivel_0": ["nxt-dev"],
    "nivel_1": ["nxt-dev", "nxt-qa"],
    "nivel_2": ["nxt-analyst", "nxt-dev", "nxt-qa", "nxt-tech-writer"],
    "nivel_3": [
        "nxt-analyst", "nxt-pm", "nxt-architect",
        "nxt-design", "nxt-dev", "nxt-qa", "nxt-tech-writer",
    ],
    "nivel_4": [
        "nxt-analyst", "nxt-pm", "nxt-architect", "nxt-design",
        "nxt-dev", "nxt-api", "nxt-database", "nxt-cybersec",
        "nxt-qa", "nxt-devops", "nxt-tech-writer",
    ],
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

class ExecutionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentStep:
    agent: str
    task: str
    status: str = ExecutionStatus.PENDING.value
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: int = 0
    artifacts: List[str] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class ExecutionPlan:
    plan_id: str
    task: str
    scale: str
    steps: List[AgentStep]
    created_at: str = ""
    status: str = ExecutionStatus.PENDING.value
    current_step: int = 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plan_id(task: str) -> str:
    """Short deterministic-ish id from task + timestamp."""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    h = hashlib.sha1(f"{task}{ts}".encode()).hexdigest()[:8]
    return f"plan-{ts}-{h}"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _step_to_dict(s: AgentStep) -> dict:
    return asdict(s)


def _plan_to_dict(p: ExecutionPlan) -> dict:
    return {
        "plan_id": p.plan_id,
        "task": p.task,
        "scale": p.scale,
        "created_at": p.created_at,
        "status": p.status,
        "current_step": p.current_step,
        "steps": [_step_to_dict(s) for s in p.steps],
    }


def _plan_from_dict(d: dict) -> ExecutionPlan:
    steps = [AgentStep(**s) for s in d.get("steps", [])]
    return ExecutionPlan(
        plan_id=d["plan_id"],
        task=d["task"],
        scale=d["scale"],
        steps=steps,
        created_at=d.get("created_at", ""),
        status=d.get("status", ExecutionStatus.PENDING.value),
        current_step=d.get("current_step", 0),
    )


# ---------------------------------------------------------------------------
# AgentExecutor
# ---------------------------------------------------------------------------

class AgentExecutor:
    """Plans and tracks agent execution sequences."""

    def __init__(self, root: Path = None):
        self.root = Path(root) if root else Path.cwd()
        self.state_dir = self.root / ".nxt"
        self.agents_dir = self.root / "agentes"
        self.checkpoints_dir = self.state_dir / "checkpoints"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

    # -- Agent discovery -----------------------------------------------------

    def list_agents(self) -> List[str]:
        """Return names of all available agents (without .md extension)."""
        if not self.agents_dir.exists():
            return []
        return sorted(p.stem for p in self.agents_dir.glob("nxt-*.md"))

    def get_agent_file(self, agent_name: str) -> Optional[Path]:
        """Get the path to an agent's markdown file."""
        name = agent_name if agent_name.endswith(".md") else f"{agent_name}.md"
        path = self.agents_dir / name
        return path if path.exists() else None

    def get_agent_instructions(self, agent_name: str) -> str:
        """Read an agent's instructions from its .md file."""
        path = self.get_agent_file(agent_name)
        if path:
            return path.read_text(encoding="utf-8")
        return ""

    # -- Plan lifecycle ------------------------------------------------------

    def create_plan(self, task: str, agents: List[str] = None, scale: str = "nivel_2") -> ExecutionPlan:
        """Create an execution plan for a sequence of agents."""
        if agents is None:
            agents = SCALE_AGENTS.get(scale, SCALE_AGENTS["nivel_2"])
        # Filter to agents that actually exist on disk
        available = set(self.list_agents())
        resolved = [a for a in agents if a in available]
        if not resolved:
            resolved = agents  # keep requested list even if files missing

        steps = [AgentStep(agent=a, task=task) for a in resolved]
        plan = ExecutionPlan(
            plan_id=_plan_id(task),
            task=task,
            scale=scale,
            steps=steps,
            created_at=_now(),
        )
        self.save_plan(plan)
        self._emit_telemetry("plan_created", {"plan_id": plan.plan_id, "scale": scale, "agents": len(steps)})
        return plan

    def start_step(self, plan: ExecutionPlan, step_index: int = None) -> AgentStep:
        """Mark a step as started."""
        idx = step_index if step_index is not None else plan.current_step
        step = plan.steps[idx]
        step.status = ExecutionStatus.IN_PROGRESS.value
        step.started_at = _now()
        plan.status = ExecutionStatus.IN_PROGRESS.value
        plan.current_step = idx
        self.save_plan(plan)
        return step

    def complete_step(self, plan: ExecutionPlan, step_index: int = None,
                      artifacts: List[str] = None) -> AgentStep:
        """Mark a step as completed with optional artifacts."""
        idx = step_index if step_index is not None else plan.current_step
        step = plan.steps[idx]
        step.status = ExecutionStatus.COMPLETED.value
        step.completed_at = _now()
        if step.started_at:
            start = datetime.fromisoformat(step.started_at)
            step.duration_ms = int((datetime.fromisoformat(step.completed_at) - start).total_seconds() * 1000)
        if artifacts:
            step.artifacts.extend(artifacts)
        # Advance pointer
        if idx + 1 < len(plan.steps):
            plan.current_step = idx + 1
        else:
            plan.status = ExecutionStatus.COMPLETED.value
        self.save_plan(plan)
        return step

    def fail_step(self, plan: ExecutionPlan, step_index: int = None, error: str = "") -> AgentStep:
        """Mark a step as failed."""
        idx = step_index if step_index is not None else plan.current_step
        step = plan.steps[idx]
        step.status = ExecutionStatus.FAILED.value
        step.completed_at = _now()
        step.error = error
        plan.status = ExecutionStatus.FAILED.value
        self.save_plan(plan)
        return step

    def skip_step(self, plan: ExecutionPlan, step_index: int = None) -> AgentStep:
        """Skip a step."""
        idx = step_index if step_index is not None else plan.current_step
        step = plan.steps[idx]
        step.status = ExecutionStatus.SKIPPED.value
        if idx + 1 < len(plan.steps):
            plan.current_step = idx + 1
        self.save_plan(plan)
        return step

    # -- Persistence ---------------------------------------------------------

    def save_plan(self, plan: ExecutionPlan):
        """Save plan as JSON in checkpoints directory."""
        path = self.checkpoints_dir / f"{plan.plan_id}.json"
        path.write_text(json.dumps(_plan_to_dict(plan), indent=2, ensure_ascii=False), encoding="utf-8")

    def load_plan(self, plan_id: str) -> Optional[ExecutionPlan]:
        """Load a plan from checkpoints."""
        path = self.checkpoints_dir / f"{plan_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return _plan_from_dict(data)

    def list_plans(self) -> List[dict]:
        """List all saved plans (summary only)."""
        plans = []
        for p in sorted(self.checkpoints_dir.glob("plan-*.json"), reverse=True):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                plans.append({
                    "plan_id": data["plan_id"],
                    "task": data["task"][:60],
                    "scale": data["scale"],
                    "status": data["status"],
                    "steps": len(data.get("steps", [])),
                    "created_at": data.get("created_at", ""),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return plans

    # -- Dry run & summary ---------------------------------------------------

    def dry_run(self, task: str, agents: List[str] = None, scale: str = "nivel_2") -> dict:
        """Simulate execution without persisting anything."""
        if agents is None:
            agents = SCALE_AGENTS.get(scale, SCALE_AGENTS["nivel_2"])
        available = set(self.list_agents())
        steps = []
        for a in agents:
            exists = a in available
            steps.append({
                "agent": a,
                "file": str(self.agents_dir / f"{a}.md") if exists else None,
                "file_exists": exists,
                "action": f"Claude reads agentes/{a}.md and executes task",
            })
        return {
            "mode": "dry-run",
            "task": task,
            "scale": scale,
            "total_agents": len(agents),
            "available_agents": sum(1 for s in steps if s["file_exists"]),
            "steps": steps,
        }

    def get_execution_summary(self, plan: ExecutionPlan) -> dict:
        """Get a summary of plan execution status."""
        by_status: Dict[str, int] = {}
        for s in plan.steps:
            by_status[s.status] = by_status.get(s.status, 0) + 1
        total_ms = sum(s.duration_ms for s in plan.steps)
        return {
            "plan_id": plan.plan_id,
            "task": plan.task,
            "scale": plan.scale,
            "status": plan.status,
            "progress": f"{plan.current_step}/{len(plan.steps)}",
            "by_status": by_status,
            "total_duration_ms": total_ms,
            "artifacts": [a for s in plan.steps for a in s.artifacts],
        }

    # -- Telemetry -----------------------------------------------------------

    def _emit_telemetry(self, event: str, data: dict = None):
        if _telemetry_emit:
            try:
                _telemetry_emit(event, data or {})
            except Exception:
                pass


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_json(obj: Any):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="NXT Agent Executor v3.8.0 - Execution planner for NXT agents",
    )
    sub = parser.add_subparsers(dest="command")

    # plan
    p_plan = sub.add_parser("plan", help="Create an execution plan")
    p_plan.add_argument("task", help="Task description")
    p_plan.add_argument("--agents", help="Comma-separated agent names (e.g. nxt-dev,nxt-qa)")
    p_plan.add_argument("--scale", default="nivel_2", choices=list(SCALE_AGENTS.keys()))

    # dry-run
    p_dry = sub.add_parser("dry-run", help="Simulate execution (no persistence)")
    p_dry.add_argument("task", help="Task description")
    p_dry.add_argument("--agents", help="Comma-separated agent names")
    p_dry.add_argument("--scale", default="nivel_2", choices=list(SCALE_AGENTS.keys()))

    # list
    sub.add_parser("list", help="List saved execution plans")

    # status
    p_status = sub.add_parser("status", help="Show plan status")
    p_status.add_argument("plan_id", help="Plan ID")

    # agents
    sub.add_parser("agents", help="List available agents")

    # execute (dry-run alias kept for backward compat)
    p_exec = sub.add_parser("execute", help="Alias for plan (backward compat)")
    p_exec.add_argument("task", help="Task description")
    p_exec.add_argument("--dry-run", action="store_true", help="Dry run mode")
    p_exec.add_argument("--agents", help="Comma-separated agent names")
    p_exec.add_argument("--scale", default="nivel_2")

    args = parser.parse_args()
    executor = AgentExecutor()

    if args.command == "plan":
        agents = [a.strip() for a in args.agents.split(",")] if args.agents else None
        plan = executor.create_plan(args.task, agents=agents, scale=args.scale)
        print(f"Plan created: {plan.plan_id}")
        _print_json(_plan_to_dict(plan))

    elif args.command == "dry-run":
        agents = [a.strip() for a in args.agents.split(",")] if args.agents else None
        result = executor.dry_run(args.task, agents=agents, scale=args.scale)
        _print_json(result)

    elif args.command == "list":
        plans = executor.list_plans()
        if not plans:
            print("No execution plans found.")
        else:
            print(f"Found {len(plans)} plan(s):\n")
            for p in plans:
                status_icon = {"completed": "+", "failed": "!", "in_progress": ">", "pending": " "}.get(p["status"], "?")
                print(f"  [{status_icon}] {p['plan_id']}  {p['scale']}  {p['status']:<12}  {p['steps']} steps  {p['task']}")

    elif args.command == "status":
        plan = executor.load_plan(args.plan_id)
        if not plan:
            print(f"Plan not found: {args.plan_id}")
            sys.exit(1)
        _print_json(executor.get_execution_summary(plan))

    elif args.command == "agents":
        agents = executor.list_agents()
        print(f"Available agents ({len(agents)}):\n")
        for a in agents:
            print(f"  - {a}")

    elif args.command == "execute":
        agents = [a.strip() for a in args.agents.split(",")] if args.agents else None
        if getattr(args, "dry_run", False):
            result = executor.dry_run(args.task, agents=agents, scale=args.scale)
            _print_json(result)
        else:
            plan = executor.create_plan(args.task, agents=agents, scale=args.scale)
            print(f"Plan created: {plan.plan_id}")
            _print_json(_plan_to_dict(plan))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
