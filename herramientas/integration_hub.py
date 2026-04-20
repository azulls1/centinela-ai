#!/usr/bin/env python3
"""
NXT AI Development - Integration Hub v3.8.0
============================================
Centro funcional de integración para los componentes del framework.

Coordina:
- Event Bus: pub/sub entre componentes
- State Manager: lectura/escritura de .nxt/state.json
- Telemetry: envío de eventos a Supabase
- Agent Registry: catálogo de agentes disponibles
- Config: acceso centralizado a nxt.config.yaml
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field

# Framework imports
try:
    from utils import get_project_root, load_config
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import get_project_root, load_config

try:
    from event_bus import EventBus, EventType, get_event_bus, emit
    HAS_EVENT_BUS = True
except ImportError:
    HAS_EVENT_BUS = False

try:
    from nxt_telemetry import track as track_telemetry
    HAS_TELEMETRY = True
except ImportError:
    HAS_TELEMETRY = False


@dataclass
class AgentInfo:
    """Información de un agente registrado."""
    name: str
    file: str
    phase: str = ""
    description: str = ""
    available: bool = True


@dataclass
class HubStatus:
    """Estado actual del hub."""
    event_bus: bool = False
    telemetry: bool = False
    state_loaded: bool = False
    config_loaded: bool = False
    agents_count: int = 0
    skills_count: int = 0


class IntegrationHub:
    """Hub central de integración del framework NXT."""

    def __init__(self, root: Path = None):
        self.root = root or Path(get_project_root())
        self.nxt_dir = self.root / ".nxt"
        self.agents_dir = self.root / "agentes"
        self.skills_dir = self.root / "skills"
        self._config: Optional[Dict] = None
        self._state: Optional[Dict] = None
        self._agents: Dict[str, AgentInfo] = {}
        self._event_bus = get_event_bus() if HAS_EVENT_BUS else None

    # =========================================================================
    # CONFIG
    # =========================================================================

    def load_config(self) -> Dict[str, Any]:
        """Carga configuración desde nxt.config.yaml."""
        if self._config is None:
            config_path = self.nxt_dir / "nxt.config.yaml"
            if config_path.exists():
                try:
                    import yaml
                    with open(config_path, encoding="utf-8") as f:
                        self._config = yaml.safe_load(f) or {}
                except ImportError:
                    self._config = load_config()
            else:
                self._config = {}
        return self._config

    def get_config(self, key: str, default: Any = None) -> Any:
        """Accede a un valor de configuración por key (dot notation)."""
        config = self.load_config()
        keys = key.split(".")
        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current

    # =========================================================================
    # STATE
    # =========================================================================

    def load_state(self) -> Dict[str, Any]:
        """Carga estado desde .nxt/state.json."""
        state_path = self.nxt_dir / "state.json"
        if state_path.exists():
            self._state = json.loads(state_path.read_text(encoding="utf-8"))
        else:
            self._state = {"framework_version": "3.8.0", "current_phase": "init"}
        return self._state

    def save_state(self, state: Dict[str, Any] = None):
        """Guarda estado a .nxt/state.json."""
        if state:
            self._state = state
        if self._state:
            self._state["last_updated"] = datetime.now().isoformat()
            state_path = self.nxt_dir / "state.json"
            state_path.write_text(
                json.dumps(self._state, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

    def get_state(self, key: str, default: Any = None) -> Any:
        """Accede a un valor del estado."""
        if self._state is None:
            self.load_state()
        return self._state.get(key, default)

    def update_state(self, updates: Dict[str, Any]):
        """Actualiza campos del estado sin sobreescribir todo."""
        if self._state is None:
            self.load_state()
        self._state.update(updates)
        self.save_state()

    # =========================================================================
    # AGENT REGISTRY
    # =========================================================================

    def discover_agents(self) -> Dict[str, AgentInfo]:
        """Descubre todos los agentes disponibles en agentes/."""
        self._agents = {}
        if self.agents_dir.exists():
            for md_file in sorted(self.agents_dir.glob("nxt-*.md")):
                name = md_file.stem  # e.g., "nxt-dev"
                # Extraer fase del contenido (primera línea con "Fase")
                phase = ""
                description = ""
                try:
                    content = md_file.read_text(encoding="utf-8")
                    for line in content.split("\n"):
                        if line.startswith("## Fase") or "**Fase**" in line or "**TRANSVERSAL**" in line:
                            phase = line.strip().replace("**", "").replace("## ", "")
                        if line.startswith("> **Rol:**"):
                            description = line.replace("> **Rol:**", "").strip()
                except Exception:
                    pass
                self._agents[name] = AgentInfo(
                    name=name, file=str(md_file.relative_to(self.root)),
                    phase=phase, description=description
                )
        return self._agents

    def get_agent(self, name: str) -> Optional[AgentInfo]:
        """Obtiene información de un agente."""
        if not self._agents:
            self.discover_agents()
        return self._agents.get(name)

    def get_agent_instructions(self, name: str) -> str:
        """Lee las instrucciones completas de un agente."""
        agent_file = self.agents_dir / f"{name}.md"
        if agent_file.exists():
            return agent_file.read_text(encoding="utf-8")
        return ""

    def list_agents(self) -> List[str]:
        """Lista nombres de todos los agentes."""
        if not self._agents:
            self.discover_agents()
        return list(self._agents.keys())

    # =========================================================================
    # SKILLS REGISTRY
    # =========================================================================

    def discover_skills(self) -> List[str]:
        """Descubre todos los skills disponibles."""
        skills = []
        if self.skills_dir.exists():
            for md_file in sorted(self.skills_dir.rglob("SKILL-*.md")):
                skills.append(str(md_file.relative_to(self.root)))
        return skills

    # =========================================================================
    # EVENT BUS
    # =========================================================================

    def emit_event(self, event_type: str, data: Dict[str, Any] = None):
        """Emite un evento al bus."""
        if self._event_bus and HAS_EVENT_BUS:
            try:
                emit(event_type, data or {})
            except Exception:
                pass

    # =========================================================================
    # TELEMETRY
    # =========================================================================

    def track(self, event_type: str, data: Dict[str, Any] = None):
        """Registra evento de telemetría."""
        if HAS_TELEMETRY:
            try:
                track_telemetry(event_type, data or {}, root=self.root)
            except Exception:
                pass

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Retorna estado completo del hub."""
        agents = self.discover_agents()
        skills = self.discover_skills()
        state = self.load_state()
        config = self.load_config()

        return {
            "hub_version": "3.8.0",
            "components": {
                "event_bus": HAS_EVENT_BUS,
                "telemetry": HAS_TELEMETRY,
                "state_loaded": self._state is not None,
                "config_loaded": self._config is not None,
            },
            "counts": {
                "agents": len(agents),
                "skills": len(skills),
                "pending_tasks": len(state.get("pending_tasks", [])),
                "completed_tasks": len(state.get("completed_tasks", [])),
            },
            "framework_version": state.get("framework_version", "unknown"),
            "current_phase": state.get("current_phase", "unknown"),
        }


# Singleton
_hub: Optional[IntegrationHub] = None

def get_hub(root: Path = None) -> IntegrationHub:
    """Obtiene instancia singleton del hub."""
    global _hub
    if _hub is None:
        _hub = IntegrationHub(root)
    return _hub


# =========================================================================
# CLI
# =========================================================================

def main():
    """CLI del Integration Hub."""
    import argparse
    parser = argparse.ArgumentParser(description="NXT Integration Hub v3.8.0")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Estado del hub")
    sub.add_parser("agents", help="Listar agentes")
    sub.add_parser("skills", help="Listar skills")

    p_agent = sub.add_parser("agent", help="Info de un agente")
    p_agent.add_argument("name", help="Nombre del agente (e.g., nxt-dev)")

    args = parser.parse_args()
    hub = get_hub()

    if args.command == "status":
        status = hub.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif args.command == "agents":
        agents = hub.discover_agents()
        print(f"\n{'Agente':<25} {'Fase':<20} {'Descripcion'}")
        print("-" * 80)
        for name, info in agents.items():
            print(f"{name:<25} {info.phase[:18]:<20} {info.description[:40]}")
        print(f"\nTotal: {len(agents)} agentes")

    elif args.command == "skills":
        skills = hub.discover_skills()
        for s in skills:
            print(f"  {s}")
        print(f"\nTotal: {len(skills)} skills")

    elif args.command == "agent":
        agent = hub.get_agent(args.name)
        if agent:
            print(json.dumps({
                "name": agent.name,
                "file": agent.file,
                "phase": agent.phase,
                "description": agent.description,
                "available": agent.available,
            }, indent=2))
        else:
            print(f"Agente '{args.name}' no encontrado")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
