#!/usr/bin/env python3
"""
Hook: on-workflow-complete
==========================
Se ejecuta cuando un workflow completa todos sus pasos.

Tareas:
- Generar resumen de ejecución
- Actualizar estado final
- Notificar completado
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


def track_telemetry(task: str, total_steps: int):
    """Registra evento de telemetría (fire-and-forget)."""
    try:
        root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(root / "herramientas"))
        from nxt_telemetry import track
        track("workflow_completed", {"task": task[:100], "total_steps": total_steps}, root=root)
    except Exception:
        pass


def main():
    """Ejecuta el hook de workflow completado."""
    context_json = os.environ.get("NXT_HOOK_CONTEXT", "{}")
    context = json.loads(context_json)

    task = context.get("task", "unknown")
    total_steps = context.get("total_steps", 0)

    track_telemetry(task, total_steps)

    print(f"[HOOK:on-workflow-complete] Workflow finished!")
    print(f"  Task: {task[:50]}..." if len(task) > 50 else f"  Task: {task}")
    print(f"  Steps executed: {total_steps}")
    print(f"  Completed at: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
