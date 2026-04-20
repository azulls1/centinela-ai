#!/usr/bin/env python3
"""
Hook: on-init
=============
Se ejecuta cuando el sistema NXT se inicializa.

Tareas:
- Validar configuración
- Cargar registros
- Verificar dependencias
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


def main():
    """Ejecuta el hook de inicialización."""
    # Obtener contexto del hook
    context_json = os.environ.get("NXT_HOOK_CONTEXT", "{}")
    context = json.loads(context_json)

    print(f"[HOOK:on-init] NXT System initializing...")
    print(f"  Version: {context.get('version', 'unknown')}")
    print(f"  Agents: {context.get('agents_count', 0)}")
    print(f"  Skills: {context.get('skills_count', 0)}")
    print(f"  Workflows: {context.get('workflows_count', 0)}")

    # Verificar archivos críticos
    root = Path(__file__).parent.parent.parent.parent
    critical_files = [
        root / ".nxt" / "nxt.config.yaml",
        root / ".nxt" / "state.json",
        root / "agentes" / "nxt-orchestrator.md",
    ]

    missing = [str(f) for f in critical_files if not f.exists()]
    if missing:
        print(f"  [WARNING] Missing files: {len(missing)}")
        for f in missing:
            print(f"    - {f}")
    else:
        print(f"  [OK] All critical files present")

    # Telemetría: registrar inicio de sesión
    try:
        sys.path.insert(0, str(root / "herramientas"))
        from nxt_telemetry import track
        track("session_start", {
            "agents_count": context.get("agents_count", 0),
            "skills_count": context.get("skills_count", 0),
        }, root=root)
    except Exception:
        pass

    print(f"[HOOK:on-init] Complete at {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
