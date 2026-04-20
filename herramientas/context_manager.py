#!/usr/bin/env python3
"""
NXT Context Manager v3.8.0 - Gestion de Contexto y Checkpoints
===============================================================

Herramienta CLI para gestionar el estado persistente del sistema NXT,
previniendo perdida de contexto en sesiones largas.

Uso:
    python context_manager.py checkpoint [mensaje]
    python context_manager.py list
    python context_manager.py show [checkpoint_id]
    python context_manager.py resume [checkpoint_id]
    python context_manager.py clean [--keep N] [--days D]
    python context_manager.py status
    python context_manager.py validate [--max-age-hours H]
    python context_manager.py should-trigger <trigger_type>

Version: 3.8.0
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

# Try to import yaml; fall back gracefully
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# Configuracion
NXT_DIR = Path(__file__).parent.parent / ".nxt"
STATE_DIR = NXT_DIR / "state"
CHECKPOINTS_DIR = NXT_DIR / "checkpoints"
SESSIONS_DIR = STATE_DIR / "sessions"
RECOVERY_DIR = STATE_DIR / "recovery"
CURRENT_STATE_FILE = STATE_DIR / "current.json"
STATE_JSON_FILE = NXT_DIR / "state.json"
SESSION_CONTEXT_FILE = NXT_DIR / "context" / "session-context.json"
CONFIG_FILE = NXT_DIR / "nxt.config.yaml"

# Crear directorios si no existen
for dir_path in [STATE_DIR, CHECKPOINTS_DIR, SESSIONS_DIR, RECOVERY_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


class ContextManager:
    """Gestor de contexto y checkpoints para NXT v3.8.0."""

    def __init__(self):
        self.state_dir = STATE_DIR
        self.checkpoints_dir = CHECKPOINTS_DIR
        self.max_checkpoints = 20

    def create_checkpoint(
        self,
        trigger: str = "manual",
        message: str = None,
        state: Dict = None
    ) -> str:
        """Crea un nuevo checkpoint."""
        timestamp = datetime.now()
        checkpoint_id = f"cp_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        # Si no hay estado proporcionado, cargar el actual
        if state is None:
            state = self._load_current_state()

        checkpoint = {
            "checkpoint_id": checkpoint_id,
            "timestamp": timestamp.isoformat(),
            "trigger": trigger,
            "message": message,
            "state": state,
            "summary": self._create_summary(state)
        }

        # Guardar checkpoint
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)

        # Actualizar last_known_good
        recovery_file = RECOVERY_DIR / "last_known_good.json"
        with open(recovery_file, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)

        # Limpiar checkpoints antiguos
        self._cleanup_old_checkpoints()

        return checkpoint_id

    def list_checkpoints(self, limit: int = 10) -> List[Dict]:
        """Lista los checkpoints disponibles.

        Handles both checkpoint files (cp_*) and plan files (plan_*/plan-*).
        """
        checkpoints = []

        for cp_file in sorted(self.checkpoints_dir.glob("*.json"), reverse=True):
            try:
                with open(cp_file, "r", encoding="utf-8") as f:
                    cp = json.load(f)

                    # Support both checkpoint and plan file formats
                    ts = cp.get("timestamp") or cp.get("created_at") or cp.get("started_at") or cp.get("checkpoint_at") or "unknown"
                    task = "N/A"
                    if isinstance(cp.get("summary"), dict):
                        task = cp["summary"].get("task", "N/A")
                    elif cp.get("task"):
                        task = cp["task"]

                    checkpoints.append({
                        "id": cp.get("checkpoint_id") or cp.get("plan_id") or cp_file.stem,
                        "timestamp": ts,
                        "trigger": cp.get("trigger") or cp.get("status") or "unknown",
                        "message": cp.get("message") or cp.get("description"),
                        "summary": task,
                        "file": str(cp_file)
                    })
            except Exception as e:
                print(f"Error leyendo {cp_file}: {e}")

            if len(checkpoints) >= limit:
                break

        return checkpoints

    def load_checkpoint(self, checkpoint_id: str = None) -> Optional[Dict]:
        """Carga un checkpoint especifico o el ultimo."""
        if checkpoint_id:
            # Try exact match first
            cp_file = self.checkpoints_dir / f"{checkpoint_id}.json"
            if not cp_file.exists():
                # Try glob match
                matches = list(self.checkpoints_dir.glob(f"*{checkpoint_id}*.json"))
                if matches:
                    cp_file = sorted(matches, reverse=True)[0]
                else:
                    return None
        else:
            # Cargar el ultimo
            cp_files = sorted(self.checkpoints_dir.glob("*.json"), reverse=True)
            if not cp_files:
                return None
            cp_file = cp_files[0]

        if not cp_file.exists():
            return None

        with open(cp_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def show_checkpoint(self, checkpoint_id: str = None) -> str:
        """Muestra un checkpoint en formato legible."""
        cp = self.load_checkpoint(checkpoint_id)
        if not cp:
            return "No se encontro el checkpoint"

        cp_id = cp.get('checkpoint_id') or cp.get('plan_id') or cp.get('id') or 'unknown'
        cp_ts = cp.get('timestamp') or cp.get('created_at') or cp.get('started_at') or 'unknown'
        cp_trigger = cp.get('trigger') or cp.get('status') or 'unknown'

        output = []
        output.append("=" * 60)
        output.append(f"CHECKPOINT: {cp_id}")
        output.append("=" * 60)
        output.append(f"Timestamp: {cp_ts}")
        output.append(f"Trigger/Status: {cp_trigger}")
        if cp.get("message"):
            output.append(f"Mensaje: {cp.get('message')}")
        if cp.get("description"):
            output.append(f"Descripcion: {cp.get('description')}")
        output.append("")

        # Handle plan format
        if "steps" in cp and "task" in cp and not cp.get("summary"):
            output.append("PLAN:")
            output.append("-" * 40)
            output.append(f"  Tarea: {cp.get('task', 'N/A')}")
            output.append(f"  Escala: {cp.get('scale', 'N/A')}")
            output.append(f"  Status: {cp.get('status', 'N/A')}")

            results = cp.get("results", [])
            if results:
                output.append(f"  Pasos completados: {len(results)}")
                for r in results:
                    dur = r.get("duration_seconds", 0)
                    output.append(f"    - {r.get('agent', '?')} ({r.get('status', '?')}, {dur:.1f}s)")

            steps = cp.get("steps", [])
            if steps:
                output.append(f"  Pasos pendientes: {len(steps)}")
                for s in steps:
                    step_name = s if isinstance(s, str) else s.get("agent", "unknown")
                    output.append(f"    - {step_name}")
        else:
            # Standard checkpoint format
            summary = cp.get("summary", {})
            if summary:
                output.append("RESUMEN:")
                output.append("-" * 40)
                output.append(f"  Tarea: {summary.get('task', 'N/A')}")
                output.append(f"  Progreso: {summary.get('progress', 'N/A')}")
                output.append(f"  Agente actual: {summary.get('current_agent', summary.get('current_action', 'N/A'))}")
                output.append(f"  Siguiente: {summary.get('next_action', 'N/A')}")

                decisions = summary.get("key_decisions", [])
                if decisions:
                    output.append(f"  Decisiones: {', '.join(str(d) for d in decisions)}")

                files = summary.get("files_created", summary.get("files_modified", []))
                if files:
                    output.append(f"  Archivos: {len(files)} modificados")

        output.append("")

        # Recovery instructions - check both locations
        recovery_instructions = cp.get("recovery_instructions", [])
        if not recovery_instructions:
            recovery_instructions = cp.get("state", {}).get("recovery_instructions", [])

        if recovery_instructions:
            output.append("INSTRUCCIONES DE RECOVERY:")
            output.append("-" * 40)
            for instruction in recovery_instructions:
                output.append(f"  {instruction}")

        return "\n".join(output)

    def resume_from_checkpoint(self, checkpoint_id: str = None) -> Dict:
        """Prepara el estado para resumir desde un checkpoint.

        Enhanced in v3.8.0:
        - Lists available checkpoints when none specified
        - Validates referenced files still exist
        - Shows detailed summary
        """
        if checkpoint_id is None:
            # Show available checkpoints to help choose
            available = self.list_checkpoints(limit=5)
            if not available:
                return {"success": False, "error": "No hay checkpoints disponibles"}

        cp = self.load_checkpoint(checkpoint_id)
        if not cp:
            return {"success": False, "error": "Checkpoint no encontrado"}

        # Validate referenced files exist
        file_validation = self._validate_checkpoint_files(cp)

        # Actualizar estado actual
        state = cp.get("state", {})
        self._save_current_state(state)

        # Generar resumen de recovery
        recovery_summary = self._generate_recovery_summary(cp)

        return {
            "success": True,
            "checkpoint_id": cp.get("checkpoint_id") or cp.get("plan_id") or cp.get("id") or "unknown",
            "timestamp": cp.get("timestamp") or cp.get("created_at") or cp.get("started_at"),
            "recovery_summary": recovery_summary,
            "file_validation": file_validation,
            "state": state
        }

    def get_status(self) -> Dict:
        """Obtiene el estado actual del sistema de contexto."""
        checkpoints = sorted(self.checkpoints_dir.glob("*.json"), reverse=True)
        current_state = self._load_current_state()

        # Calcular tamano total
        total_size = sum(f.stat().st_size for f in checkpoints)

        # Latest checkpoint age
        latest_age_hours = None
        if checkpoints:
            try:
                with open(checkpoints[0], "r", encoding="utf-8") as f:
                    latest_cp = json.load(f)
                ts = latest_cp.get("timestamp", "")
                if ts:
                    cp_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    now = datetime.now(cp_time.tzinfo) if cp_time.tzinfo else datetime.now()
                    latest_age_hours = round((now - cp_time).total_seconds() / 3600, 1)
            except Exception:
                pass

        return {
            "checkpoints_count": len(checkpoints),
            "total_size_kb": round(total_size / 1024, 2),
            "latest_checkpoint": checkpoints[0].stem if checkpoints else None,
            "latest_age_hours": latest_age_hours,
            "state_json_exists": STATE_JSON_FILE.exists(),
            "session_context_exists": SESSION_CONTEXT_FILE.exists(),
            "current_state": {
                "has_state": bool(current_state),
                "task": current_state.get("orchestrator", {}).get("current_task"),
                "phase": current_state.get("orchestrator", {}).get("progress", {}).get("phase")
            } if current_state else None
        }

    def validate(self, max_age_hours: float = 24.0) -> Dict:
        """Validates the health of the context/checkpoint system.

        Checks:
        - state.json exists and is valid JSON
        - checkpoints directory exists and has checkpoints
        - Latest checkpoint is not older than max_age_hours
        - session-context.json exists and is valid JSON

        Returns dict with 'healthy' bool and list of 'issues'.
        """
        issues = []
        warnings = []

        # 1. state.json
        if STATE_JSON_FILE.exists():
            try:
                with open(STATE_JSON_FILE, "r", encoding="utf-8") as f:
                    state_data = json.load(f)
                if not isinstance(state_data, dict):
                    issues.append("state.json is not a JSON object")
                else:
                    # Check required keys
                    expected_keys = ["framework_version", "current_phase"]
                    missing = [k for k in expected_keys if k not in state_data]
                    if missing:
                        warnings.append(f"state.json missing keys: {', '.join(missing)}")
            except json.JSONDecodeError as e:
                issues.append(f"state.json is invalid JSON: {e}")
            except Exception as e:
                issues.append(f"state.json unreadable: {e}")
        else:
            issues.append(f"state.json not found at {STATE_JSON_FILE}")

        # 2. Checkpoints directory
        if CHECKPOINTS_DIR.exists():
            cp_files = sorted(CHECKPOINTS_DIR.glob("*.json"), reverse=True)
            if not cp_files:
                warnings.append("Checkpoints directory is empty (no .json files)")
            else:
                # Check latest checkpoint age
                try:
                    with open(cp_files[0], "r", encoding="utf-8") as f:
                        latest = json.load(f)
                    ts = latest.get("timestamp", "")
                    if ts:
                        cp_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        now = datetime.now(cp_time.tzinfo) if cp_time.tzinfo else datetime.now()
                        age_hours = (now - cp_time).total_seconds() / 3600
                        if age_hours > max_age_hours:
                            warnings.append(
                                f"Latest checkpoint is {age_hours:.1f}h old "
                                f"(threshold: {max_age_hours}h) - {cp_files[0].name}"
                            )
                except Exception as e:
                    warnings.append(f"Could not parse latest checkpoint timestamp: {e}")

                # Validate each checkpoint is valid JSON
                invalid_count = 0
                for cp_file in cp_files:
                    try:
                        with open(cp_file, "r", encoding="utf-8") as f:
                            json.load(f)
                    except Exception:
                        invalid_count += 1
                if invalid_count:
                    issues.append(f"{invalid_count} checkpoint(s) contain invalid JSON")
        else:
            issues.append(f"Checkpoints directory not found at {CHECKPOINTS_DIR}")

        # 3. session-context.json
        if SESSION_CONTEXT_FILE.exists():
            try:
                with open(SESSION_CONTEXT_FILE, "r", encoding="utf-8") as f:
                    ctx = json.load(f)
                if not isinstance(ctx, dict):
                    warnings.append("session-context.json is not a JSON object")
            except json.JSONDecodeError as e:
                issues.append(f"session-context.json is invalid JSON: {e}")
            except Exception as e:
                issues.append(f"session-context.json unreadable: {e}")
        else:
            warnings.append(f"session-context.json not found at {SESSION_CONTEXT_FILE}")

        # 4. current.json (state dir)
        if CURRENT_STATE_FILE.exists():
            try:
                with open(CURRENT_STATE_FILE, "r", encoding="utf-8") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                issues.append(f"state/current.json is invalid JSON: {e}")
        else:
            warnings.append(f"state/current.json not found")

        healthy = len(issues) == 0
        return {
            "healthy": healthy,
            "issues": issues,
            "warnings": warnings,
            "checks_passed": 4 - len(issues),
            "checks_total": 4
        }

    def clean_checkpoints(self, keep: int = 20, max_days: int = 7) -> Dict:
        """Cleans old checkpoints.

        Strategy:
        1. Remove checkpoints older than max_days
        2. After age-based removal, keep at most 'keep' latest checkpoints
        3. Report what was cleaned

        Returns dict with counts and details.
        """
        all_files = sorted(self.checkpoints_dir.glob("*.json"), reverse=True)
        if not all_files:
            return {"deleted": 0, "kept": 0, "details": []}

        cutoff = datetime.now() - timedelta(days=max_days)
        deleted_by_age = []
        deleted_by_count = []
        kept = []

        # First pass: separate by age
        for cp_file in all_files:
            file_age = None
            try:
                with open(cp_file, "r", encoding="utf-8") as f:
                    cp_data = json.load(f)
                ts = cp_data.get("timestamp", "")
                if ts:
                    cp_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if cp_time.tzinfo:
                        file_age = cp_time.replace(tzinfo=None)
                    else:
                        file_age = cp_time
            except Exception:
                # Fall back to file modification time
                file_age = datetime.fromtimestamp(cp_file.stat().st_mtime)

            if file_age and file_age < cutoff:
                deleted_by_age.append(cp_file)
            else:
                kept.append(cp_file)

        # Second pass: enforce max count on remaining
        if len(kept) > keep:
            deleted_by_count = kept[keep:]
            kept = kept[:keep]

        # Perform deletions
        details = []
        for cp_file in deleted_by_age:
            cp_file.unlink()
            details.append(f"[age>{max_days}d] {cp_file.name}")

        for cp_file in deleted_by_count:
            cp_file.unlink()
            details.append(f"[overflow>{keep}] {cp_file.name}")

        total_deleted = len(deleted_by_age) + len(deleted_by_count)
        return {
            "deleted": total_deleted,
            "deleted_by_age": len(deleted_by_age),
            "deleted_by_count": len(deleted_by_count),
            "kept": len(kept),
            "details": details
        }

    def should_trigger(self, trigger_type: str) -> Dict:
        """Determines which persistence agents should run for a given trigger.

        Reads the persistencia section of nxt.config.yaml and returns
        matching agents for the specified trigger type.

        Args:
            trigger_type: One of 'always', 'on_session_start', 'on_task_complete',
                         'on_agent_switch', 'on_checkpoint', 'on_session_end',
                         'on_every_interaction'

        Returns:
            Dict with 'should_run' bool, 'agents' list, and 'trigger' info.
        """
        config = self._load_config()
        if not config:
            return {
                "should_run": False,
                "agents": [],
                "trigger": trigger_type,
                "error": "Could not load nxt.config.yaml"
            }

        persistencia = config.get("persistencia", {})
        if not persistencia.get("habilitado", False):
            return {
                "should_run": False,
                "agents": [],
                "trigger": trigger_type,
                "reason": "Persistence is disabled in config"
            }

        # Get agents from the triggers map
        triggers_map = persistencia.get("triggers", {})
        agents_for_trigger = triggers_map.get(trigger_type, [])

        # If trigger is 'always' or 'on_every_interaction', include all persistence agents
        if trigger_type in ("always", "on_every_interaction") and not agents_for_trigger:
            agents_for_trigger = [
                a.get("nombre", "") for a in persistencia.get("agentes", [])
            ]

        # Enrich with agent details
        agent_details = []
        all_agents = {a["nombre"]: a for a in persistencia.get("agentes", []) if "nombre" in a}
        for agent_name in agents_for_trigger:
            info = all_agents.get(agent_name, {})
            agent_details.append({
                "nombre": agent_name,
                "archivo": info.get("archivo", f"agentes/{agent_name}.md"),
                "proposito": info.get("proposito", ""),
            })

        return {
            "should_run": len(agents_for_trigger) > 0,
            "agents": agents_for_trigger,
            "agent_details": agent_details,
            "trigger": trigger_type,
            "all_triggers": list(triggers_map.keys())
        }

    # ─────────────────────────────────────────────────────────────────────
    # Private helpers
    # ─────────────────────────────────────────────────────────────────────

    def _load_config(self) -> Optional[Dict]:
        """Load nxt.config.yaml, returns None if unavailable."""
        if not CONFIG_FILE.exists():
            return None

        if HAS_YAML:
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception:
                return None
        else:
            # Minimal YAML parser for the persistencia section
            return self._parse_yaml_minimal(CONFIG_FILE)

    def _parse_yaml_minimal(self, filepath: Path) -> Optional[Dict]:
        """Minimal YAML-like parser for nxt.config.yaml when PyYAML is absent.

        Handles enough structure to extract the persistencia.triggers section.
        Falls back to reading state.json persistence_agents for trigger info.
        """
        try:
            # Use state.json as a reliable fallback source
            if STATE_JSON_FILE.exists():
                with open(STATE_JSON_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)

                pa = state.get("persistence_agents", {})
                if pa:
                    # Reconstruct a config-like dict from state.json
                    return {
                        "persistencia": {
                            "habilitado": pa.get("enabled", True),
                            "agentes": [
                                {"nombre": name, "archivo": f"agentes/{name}.md"}
                                for name in pa.get("agents", [])
                            ],
                            "triggers": {
                                trigger: pa.get("agents", [])
                                for trigger in pa.get("triggers", [])
                            }
                        }
                    }
            return None
        except Exception:
            return None

    def _validate_checkpoint_files(self, checkpoint: Dict) -> Dict:
        """Validate that files referenced in a checkpoint still exist."""
        state = checkpoint.get("state", {})
        artifacts = state.get("artifacts", {})

        files_created = artifacts.get("files_created", [])
        files_modified = artifacts.get("files_modified", [])
        all_files = list(set(files_created + files_modified))

        if not all_files:
            return {"checked": 0, "existing": 0, "missing": []}

        project_root = NXT_DIR.parent
        missing = []
        existing = 0

        for filepath in all_files:
            full_path = project_root / filepath
            if full_path.exists():
                existing += 1
            else:
                missing.append(filepath)

        return {
            "checked": len(all_files),
            "existing": existing,
            "missing": missing
        }

    def _load_current_state(self) -> Dict:
        """Carga el estado actual."""
        if CURRENT_STATE_FILE.exists():
            try:
                with open(CURRENT_STATE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception):
                return {}
        return {}

    def _save_current_state(self, state: Dict):
        """Guarda el estado actual."""
        with open(CURRENT_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def _create_summary(self, state: Dict) -> Dict:
        """Crea un resumen del estado."""
        orchestrator = state.get("orchestrator", {})
        agents = state.get("agents", {})
        artifacts = state.get("artifacts", {})
        decisions = state.get("decisions", [])

        progress = orchestrator.get("progress", {})
        percentage = "N/A"
        if progress.get("total_steps"):
            percentage = f"{(progress.get('step', 0) / progress.get('total_steps')) * 100:.1f}%"

        return {
            "task": orchestrator.get("current_task", "N/A"),
            "progress": percentage,
            "current_agent": agents.get("current", "N/A"),
            "next_action": artifacts.get("pending_files", ["N/A"])[0] if artifacts.get("pending_files") else "N/A",
            "key_decisions": [d.get("value", d.get("answer", d.get("summary", ""))) for d in decisions[:5]],
            "files_created": artifacts.get("files_created", []),
            "files_modified": artifacts.get("files_modified", [])
        }

    def _generate_recovery_summary(self, checkpoint: Dict) -> str:
        """Genera un resumen para recovery.

        Handles both checkpoint format (with summary/state) and plan format
        (with task/steps/results).
        """
        summary = checkpoint.get("summary", {})
        state = checkpoint.get("state", {})

        # Detect plan format vs checkpoint format
        is_plan = "steps" in checkpoint and "task" in checkpoint and not summary

        lines = []
        lines.append("## SESSION RECOVERY SUMMARY")
        lines.append("")

        if is_plan:
            # Plan file format
            lines.append(f"### Tarea Principal")
            lines.append(f"{checkpoint.get('task', 'N/A')}")
            lines.append("")
            lines.append(f"### Estado del Plan")
            lines.append(f"- Status: {checkpoint.get('status', 'N/A')}")
            lines.append(f"- Escala: {checkpoint.get('scale', 'N/A')}")
            lines.append("")

            # Steps info
            results = checkpoint.get("results", [])
            steps = checkpoint.get("steps", [])
            if results:
                lines.append(f"### Pasos Ejecutados ({len(results)} completados)")
                for r in results:
                    status_icon = "[OK]" if r.get("status") == "completed" else "[--]"
                    lines.append(f"- {status_icon} {r.get('agent', r.get('step', 'unknown'))}")
            if steps:
                lines.append(f"### Pasos Pendientes")
                for step in steps:
                    step_name = step if isinstance(step, str) else step.get("agent", "unknown")
                    lines.append(f"- {step_name}")
        else:
            # Standard checkpoint format
            task = summary.get('task', 'N/A')
            if task == 'N/A' and checkpoint.get('task'):
                task = checkpoint['task']

            lines.append(f"### Tarea Principal")
            lines.append(f"{task}")
            lines.append("")
            lines.append(f"### Progreso")
            lines.append(f"- Progreso: {summary.get('progress', 'N/A')}")
            lines.append(f"- Agente actual: {summary.get('current_agent', summary.get('current_action', 'N/A'))}")
            lines.append("")
            lines.append(f"### Decisiones Clave")
            for decision in summary.get("key_decisions", []):
                lines.append(f"- {decision}")
            lines.append("")
            lines.append(f"### Archivos Creados/Modificados")
            for file in summary.get("files_created", []):
                lines.append(f"- [created] {file}")
            for file in summary.get("files_modified", []):
                lines.append(f"- [modified] {file}")
            lines.append("")
            lines.append(f"### Siguiente Paso")
            lines.append(f"{summary.get('next_action', 'N/A')}")

        # Recovery instructions
        recovery_instructions = checkpoint.get("recovery_instructions", [])
        if not recovery_instructions:
            recovery_instructions = state.get("recovery_instructions", [])
        if recovery_instructions:
            lines.append("")
            lines.append("### Instrucciones de Recovery")
            for instr in recovery_instructions:
                lines.append(f"- {instr}")

        return "\n".join(lines)

    def _cleanup_old_checkpoints(self):
        """Limpia checkpoints que excedan el maximo."""
        checkpoints = sorted(self.checkpoints_dir.glob("*.json"), reverse=True)
        for cp_file in checkpoints[self.max_checkpoints:]:
            cp_file.unlink()


def main():
    parser = argparse.ArgumentParser(
        description="NXT Context Manager v3.8.0 - Gestion de contexto y checkpoints"
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # Checkpoint
    cp_parser = subparsers.add_parser("checkpoint", help="Crear un checkpoint")
    cp_parser.add_argument("message", nargs="?", help="Mensaje descriptivo")

    # List
    list_parser = subparsers.add_parser("list", help="Listar checkpoints")
    list_parser.add_argument("--limit", type=int, default=10, help="Limite de resultados")

    # Show
    show_parser = subparsers.add_parser("show", help="Mostrar un checkpoint")
    show_parser.add_argument("checkpoint_id", nargs="?", help="ID del checkpoint")

    # Resume
    resume_parser = subparsers.add_parser("resume", help="Resumir desde checkpoint")
    resume_parser.add_argument("checkpoint_id", nargs="?", help="ID del checkpoint")

    # Clean
    clean_parser = subparsers.add_parser("clean", help="Limpiar checkpoints antiguos")
    clean_parser.add_argument("--keep", type=int, default=20, help="Checkpoints a mantener (default: 20)")
    clean_parser.add_argument("--days", type=int, default=7, help="Eliminar checkpoints mas viejos que N dias (default: 7)")

    # Status
    subparsers.add_parser("status", help="Ver estado del sistema")

    # Validate (NEW v3.8.0)
    validate_parser = subparsers.add_parser("validate", help="Validar salud del sistema de contexto")
    validate_parser.add_argument("--max-age-hours", type=float, default=24.0,
                                  help="Alerta si el ultimo checkpoint es mas viejo que N horas (default: 24)")

    # Should-trigger (NEW v3.8.0)
    trigger_parser = subparsers.add_parser("should-trigger", help="Verificar que agentes deben ejecutarse para un trigger")
    trigger_parser.add_argument("trigger_type", help="Tipo de trigger (always, on_session_start, on_task_complete, etc.)")

    args = parser.parse_args()
    manager = ContextManager()

    if args.command == "checkpoint":
        cp_id = manager.create_checkpoint(
            trigger="manual",
            message=args.message
        )
        print(f"Checkpoint creado: {cp_id}")

    elif args.command == "list":
        checkpoints = manager.list_checkpoints(limit=args.limit)
        if not checkpoints:
            print("No hay checkpoints disponibles")
        else:
            print(f"{'ID':<30} {'Timestamp':<25} {'Trigger':<20} {'Tarea'}")
            print("-" * 100)
            for cp in checkpoints:
                task_str = str(cp['summary'])[:35] if cp['summary'] else "N/A"
                ts_str = str(cp['timestamp'])[:19] if cp['timestamp'] else "unknown"
                print(f"{cp['id']:<30} {ts_str:<25} {cp['trigger']:<20} {task_str}")

    elif args.command == "show":
        print(manager.show_checkpoint(args.checkpoint_id))

    elif args.command == "resume":
        # Enhanced: show available checkpoints if none specified
        if not args.checkpoint_id:
            print("Checkpoints disponibles:")
            print("-" * 80)
            checkpoints = manager.list_checkpoints(limit=5)
            for i, cp in enumerate(checkpoints):
                marker = " (latest)" if i == 0 else ""
                ts_str = str(cp['timestamp'])[:19] if cp['timestamp'] else "unknown"
                print(f"  {cp['id']}  [{ts_str}]  {cp['summary']}{marker}")
            print("")
            print("Resumiendo desde el checkpoint mas reciente...")
            print("")

        result = manager.resume_from_checkpoint(args.checkpoint_id)
        if result["success"]:
            print(f"Estado cargado desde checkpoint")
            print(f"  ID: {result['checkpoint_id']}")
            print(f"  Timestamp: {result['timestamp']}")

            # File validation results
            fv = result.get("file_validation", {})
            if fv.get("checked", 0) > 0:
                print(f"  Archivos referenciados: {fv['checked']} ({fv['existing']} existen)")
                if fv.get("missing"):
                    print(f"  ADVERTENCIA - Archivos faltantes:")
                    for mf in fv["missing"]:
                        print(f"    - {mf}")
            print("")
            print(result["recovery_summary"])
        else:
            print(f"Error: {result['error']}")

    elif args.command == "clean":
        result = manager.clean_checkpoints(keep=args.keep, max_days=args.days)
        print(f"Limpieza completada:")
        print(f"  Eliminados: {result['deleted']} checkpoints")
        print(f"    - Por antigueedad (>{args.days} dias): {result['deleted_by_age']}")
        print(f"    - Por exceso (>{args.keep} max): {result['deleted_by_count']}")
        print(f"  Conservados: {result['kept']} checkpoints")
        if result['details']:
            print("")
            print("  Detalle:")
            for detail in result['details']:
                print(f"    {detail}")

    elif args.command == "status":
        status = manager.get_status()
        print("NXT Context Manager v3.8.0 - Status")
        print("=" * 45)
        print(f"  Checkpoints: {status['checkpoints_count']}")
        print(f"  Tamano total: {status['total_size_kb']} KB")
        print(f"  Ultimo checkpoint: {status['latest_checkpoint'] or 'ninguno'}")
        if status.get('latest_age_hours') is not None:
            print(f"  Edad ultimo checkpoint: {status['latest_age_hours']}h")
        print(f"  state.json: {'OK' if status['state_json_exists'] else 'FALTA'}")
        print(f"  session-context.json: {'OK' if status['session_context_exists'] else 'FALTA'}")
        if status.get("current_state"):
            cs = status["current_state"]
            print(f"  Tarea actual: {cs.get('task', 'N/A')}")
            print(f"  Fase actual: {cs.get('phase', 'N/A')}")

    elif args.command == "validate":
        result = manager.validate(max_age_hours=args.max_age_hours)
        if result["healthy"]:
            print(f"HEALTHY - {result['checks_passed']}/{result['checks_total']} checks passed")
        else:
            print(f"UNHEALTHY - {result['checks_passed']}/{result['checks_total']} checks passed")

        if result["issues"]:
            print("")
            print("ISSUES (must fix):")
            for issue in result["issues"]:
                print(f"  [ERROR] {issue}")

        if result["warnings"]:
            print("")
            print("WARNINGS:")
            for warning in result["warnings"]:
                print(f"  [WARN] {warning}")

        if not result["issues"] and not result["warnings"]:
            print("  All checks passed, no warnings.")

    elif args.command == "should-trigger":
        result = manager.should_trigger(args.trigger_type)
        if result.get("error"):
            print(f"Error: {result['error']}")
        elif result["should_run"]:
            print(f"Trigger: {result['trigger']}")
            print(f"Should run: YES")
            print(f"Agents ({len(result['agents'])}):")
            for detail in result.get("agent_details", []):
                print(f"  - {detail['nombre']}: {detail['proposito']}")
                print(f"    archivo: {detail['archivo']}")
            print("")
            print(f"Available triggers: {', '.join(result.get('all_triggers', []))}")
        else:
            reason = result.get("reason", f"No agents configured for trigger '{result['trigger']}'")
            print(f"Trigger: {result['trigger']}")
            print(f"Should run: NO")
            print(f"Reason: {reason}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
