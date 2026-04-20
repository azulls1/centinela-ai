#!/usr/bin/env python3
"""
Hook: on-agent-switch
=====================
Se ejecuta cuando se cambia de un agente a otro.

Tareas:
- Guardar contexto del agente anterior
- Preparar contexto para el nuevo agente
- Notificar cambio
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


def track_telemetry(agent: str, task: str):
    """Registra evento de telemetría (fire-and-forget)."""
    try:
        root = Path(__file__).parent.parent.parent.parent
        sys.path.insert(0, str(root / "herramientas"))
        from nxt_telemetry import track
        track("agent_activated", {"agent": agent, "task": task[:100]}, root=root)
    except Exception:
        pass


def main():
    """Ejecuta el hook de cambio de agente."""
    context_json = os.environ.get("NXT_HOOK_CONTEXT", "{}")
    context = json.loads(context_json)

    agent = context.get("agent", "unknown")
    task = context.get("task", "")

    track_telemetry(agent, task)

    print(f"[HOOK:on-agent-switch] Switching to: {agent}")
    print(f"  Task: {task[:50]}..." if len(task) > 50 else f"  Task: {task}")
    print(f"  Time: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
