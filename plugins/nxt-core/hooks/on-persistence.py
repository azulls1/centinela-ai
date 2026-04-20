#!/usr/bin/env python3
"""
Hook: on-persistence
====================
Se ejecuta para activar los agentes de persistencia automáticamente.

Este hook es parte del sistema v3.5.1 que garantiza que los agentes
de contexto, changelog, multicontext y ralph se ejecuten en cada sesión.

Agentes de Persistencia:
- nxt-context: Gestión de contexto entre sesiones
- nxt-multicontext: Checkpoints y recovery automático
- nxt-changelog: Documentación automática de cambios
- nxt-ralph: Desarrollo autónomo iterativo

Triggers:
- on_session_start: Al iniciar sesión
- on_task_complete: Al completar tarea
- on_agent_switch: Al cambiar de agente
- on_checkpoint: Al crear checkpoint
- on_session_end: Al terminar sesión
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


# Agentes de persistencia
PERSISTENCE_AGENTS = [
    "nxt-context",
    "nxt-multicontext",
    "nxt-changelog",
    "nxt-ralph",
]

# Triggers y sus agentes
PERSISTENCE_TRIGGERS = {
    "on_session_start": ["nxt-context", "nxt-multicontext"],
    "on_task_complete": ["nxt-changelog", "nxt-context"],
    "on_agent_switch": ["nxt-multicontext"],
    "on_checkpoint": ["nxt-multicontext", "nxt-ralph"],
    "on_session_end": ["nxt-context", "nxt-changelog"],
    "always": ["nxt-context"],
}


def get_project_root() -> Path:
    """Obtiene la raíz del proyecto."""
    return Path(__file__).parent.parent.parent.parent


def get_agents_to_run(trigger: str) -> list:
    """
    Obtiene los agentes a ejecutar según el trigger.

    Args:
        trigger: Nombre del trigger

    Returns:
        Lista de agentes a ejecutar
    """
    agents = PERSISTENCE_TRIGGERS.get(trigger, [])

    # Siempre incluir agentes "always"
    always_agents = PERSISTENCE_TRIGGERS.get("always", [])
    for agent in always_agents:
        if agent not in agents:
            agents.append(agent)

    return agents


def log_persistence_action(trigger: str, agents: list, root: Path):
    """
    Registra la acción de persistencia en el log.

    Args:
        trigger: Nombre del trigger
        agents: Agentes ejecutados
        root: Raíz del proyecto
    """
    log_file = root / ".nxt" / "persistence.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "trigger": trigger,
        "agents": agents,
        "status": "triggered"
    }

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def generate_instructions(agents: list, root: Path) -> dict:
    """
    Genera instrucciones para ejecutar los agentes.

    Args:
        agents: Lista de agentes
        root: Raíz del proyecto

    Returns:
        Diccionario con instrucciones
    """
    instructions = {
        "agents": [],
        "execution_order": agents,
        "files_to_read": []
    }

    for agent in agents:
        agent_file = root / "agentes" / f"{agent}.md"
        if agent_file.exists():
            instructions["agents"].append({
                "name": agent,
                "file": str(agent_file),
                "slash_command": f"/nxt/{agent.replace('nxt-', '')}",
                "exists": True
            })
            instructions["files_to_read"].append(str(agent_file))
        else:
            instructions["agents"].append({
                "name": agent,
                "file": str(agent_file),
                "slash_command": f"/nxt/{agent.replace('nxt-', '')}",
                "exists": False
            })

    return instructions


def main():
    """Ejecuta el hook de persistencia."""
    # Obtener contexto del hook
    context_json = os.environ.get("NXT_HOOK_CONTEXT", "{}")
    context = json.loads(context_json)

    trigger = context.get("trigger", "always")
    root = get_project_root()

    print(f"\n[HOOK:on-persistence] Activando agentes de persistencia...")
    print(f"  Trigger: {trigger}")
    print(f"  Timestamp: {datetime.now().isoformat()}")

    # Obtener agentes a ejecutar
    agents = get_agents_to_run(trigger)

    print(f"\n  Agentes a ejecutar ({len(agents)}):")
    for agent in agents:
        agent_file = root / "agentes" / f"{agent}.md"
        status = "[OK]" if agent_file.exists() else "[MISSING]"
        print(f"    {status} {agent}")

    # Registrar acción
    log_persistence_action(trigger, agents, root)

    # Generar instrucciones
    instructions = generate_instructions(agents, root)

    print(f"\n  Instrucciones para Claude:")
    print(f"  ---------------------------")
    for agent_info in instructions["agents"]:
        if agent_info["exists"]:
            print(f"    1. Leer: {agent_info['file']}")
            print(f"    2. O usar: {agent_info['slash_command']}")

    # Guardar instrucciones para Claude
    instructions_file = root / ".nxt" / "persistence_instructions.json"
    with open(instructions_file, "w", encoding="utf-8") as f:
        json.dump(instructions, f, indent=2, ensure_ascii=False)

    print(f"\n  Instrucciones guardadas en: {instructions_file}")
    print(f"\n[HOOK:on-persistence] Completado")

    # Retornar instrucciones como JSON para integración
    return instructions


if __name__ == "__main__":
    result = main()
    # Imprimir JSON para captura por el orquestador
    print("\n--- JSON OUTPUT ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))
