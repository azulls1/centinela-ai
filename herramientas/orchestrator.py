#!/usr/bin/env python3
"""
NXT AI Development - Multi-Agent Orchestrator
Patron: LangGraph + CrewAI + BMAD v6

Orquestacion inteligente de agentes con:
- Flujos como grafos
- Memoria persistente
- Delegacion por roles
- Inteligencia adaptativa por escala
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
from enum import Enum

# Importar utilidades locales
try:
    from utils import get_project_root, load_config, NXTContext
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import get_project_root, load_config, NXTContext


class TaskScale(Enum):
    """Escala de tarea segun BMAD v6."""
    BUG_FIX = "bug_fix"      # < 1h, 1-2 agentes
    FEATURE = "feature"       # 1-8h, 2-4 agentes
    EPIC = "epic"            # 8-40h, full team
    ENTERPRISE = "enterprise" # 40h+, multi-team


class AgentRole(Enum):
    """Roles de agentes disponibles."""
    ORCHESTRATOR = "nxt-orchestrator"
    ANALYST = "nxt-analyst"
    PM = "nxt-pm"
    ARCHITECT = "nxt-architect"
    UX = "nxt-ux"
    DEV = "nxt-dev"
    QA = "nxt-qa"
    TECH_WRITER = "nxt-tech-writer"
    SCRUM_MASTER = "nxt-scrum-master"
    DEVOPS = "nxt-devops"
    SEARCH = "nxt-search"
    MEDIA = "nxt-media"


class TaskType(Enum):
    """Tipos de tarea para delegacion."""
    RESEARCH = "research"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    DOCUMENTATION = "documentation"
    MULTIMEDIA = "multimedia"
    INFRASTRUCTURE = "infrastructure"


class MultiAgentOrchestrator:
    """Orquestador multi-agente con patrones modernos."""

    def __init__(self):
        """Inicializa el orquestador."""
        self.root = get_project_root()
        self.config = load_config()
        self.state = self._load_state()
        self.agents = self._load_agents()

    def _load_state(self) -> Dict[str, Any]:
        """Carga el estado persistente del proyecto."""
        state_file = self.root / ".nxt" / "state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "current_phase": "init",
            "completed_tasks": [],
            "pending_tasks": [],
            "active_agents": [],
            "decisions_log": [],
            "session_history": []
        }

    def _save_state(self):
        """Guarda el estado persistente."""
        state_file = self.root / ".nxt" / "state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def _load_agents(self) -> Dict[str, Dict]:
        """Carga la configuracion de agentes."""
        agents = {}
        agents_dir = self.root / "agentes"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("nxt-*.md"):
                agent_name = agent_file.stem
                agents[agent_name] = {
                    "file": str(agent_file),
                    "name": agent_name,
                    "active": False
                }
        return agents

    def classify_scale(self, task_description: str,
                       estimated_files: int = 0,
                       estimated_hours: float = 0) -> TaskScale:
        """
        Clasifica la escala de una tarea (BMAD v6 pattern).

        Args:
            task_description: Descripcion de la tarea
            estimated_files: Numero estimado de archivos a modificar
            estimated_hours: Horas estimadas de trabajo

        Returns:
            TaskScale apropiada
        """
        # Heuristicas de clasificacion
        keywords_bug = ["fix", "bug", "error", "typo", "hotfix", "patch", "corregir"]
        keywords_feature = ["add", "create", "implement", "new", "crear", "agregar", "anadir", "implementar"]
        keywords_epic = ["refactor", "migrate", "redesign", "overhaul", "sistema", "modulo", "authentication", "autenticacion"]
        keywords_enterprise = ["architecture", "platform", "infrastructure", "arquitectura", "plataforma", "microservices"]

        task_lower = task_description.lower()

        # Por palabras clave - orden de prioridad inverso
        # Enterprise primero
        if any(kw in task_lower for kw in keywords_enterprise):
            return TaskScale.ENTERPRISE

        # Epic segundo
        if any(kw in task_lower for kw in keywords_epic):
            return TaskScale.EPIC

        # Bug fix solo si tiene keywords especificos
        if any(kw in task_lower for kw in keywords_bug):
            if estimated_files <= 3 and estimated_hours < 1:
                return TaskScale.BUG_FIX

        # Feature si tiene keywords de creacion
        if any(kw in task_lower for kw in keywords_feature):
            return TaskScale.FEATURE

        # Por metricas
        if estimated_hours > 40 or estimated_files > 50:
            return TaskScale.ENTERPRISE
        elif estimated_hours > 8 or estimated_files > 20:
            return TaskScale.EPIC
        elif estimated_hours > 1 or estimated_files > 5:
            return TaskScale.FEATURE
        else:
            return TaskScale.FEATURE  # Default a feature, no bug_fix

    def delegate(self, task_type: TaskType,
                 is_external: bool = False,
                 is_technical: bool = True) -> AgentRole:
        """
        Delega una tarea al agente apropiado (CrewAI pattern).

        Args:
            task_type: Tipo de tarea
            is_external: Si requiere recursos externos
            is_technical: Si es tecnica vs orientada a usuario

        Returns:
            AgentRole del agente delegado
        """
        delegation_map = {
            TaskType.RESEARCH: AgentRole.SEARCH if is_external else AgentRole.ANALYST,
            TaskType.DESIGN: AgentRole.ARCHITECT if is_technical else AgentRole.UX,
            TaskType.IMPLEMENTATION: AgentRole.DEV,
            TaskType.VALIDATION: AgentRole.QA,
            TaskType.DOCUMENTATION: AgentRole.TECH_WRITER,
            TaskType.MULTIMEDIA: AgentRole.MEDIA,
            TaskType.INFRASTRUCTURE: AgentRole.DEVOPS,
        }

        return delegation_map.get(task_type, AgentRole.PM)

    def get_workflow_graph(self, scale: TaskScale) -> Dict[str, List[str]]:
        """
        Genera el grafo de workflow segun escala (LangGraph pattern).

        Args:
            scale: Escala de la tarea

        Returns:
            Grafo como diccionario de nodo -> [nodos_siguientes]
        """
        graphs = {
            TaskScale.BUG_FIX: {
                "start": ["dev"],
                "dev": ["qa"],
                "qa": ["end"]
            },
            TaskScale.FEATURE: {
                "start": ["analyst"],
                "analyst": ["dev"],
                "dev": ["qa"],
                "qa": ["docs"],
                "docs": ["end"]
            },
            TaskScale.EPIC: {
                "start": ["analyst"],
                "analyst": ["pm"],
                "pm": ["architect", "ux"],
                "architect": ["dev"],
                "ux": ["dev"],
                "dev": ["qa"],
                "qa": ["docs"],
                "docs": ["end"]
            },
            TaskScale.ENTERPRISE: {
                "start": ["analyst"],
                "analyst": ["pm"],
                "pm": ["architect", "ux", "devops"],
                "architect": ["dev"],
                "ux": ["dev"],
                "devops": ["dev"],
                "dev": ["qa"],
                "qa": ["docs", "devops_deploy"],
                "docs": ["end"],
                "devops_deploy": ["end"]
            }
        }

        return graphs.get(scale, graphs[TaskScale.FEATURE])

    def get_agents_for_scale(self, scale: TaskScale) -> List[AgentRole]:
        """
        Obtiene los agentes necesarios segun escala.

        Args:
            scale: Escala de la tarea

        Returns:
            Lista de agentes a involucrar
        """
        agents_map = {
            TaskScale.BUG_FIX: [
                AgentRole.DEV,
                AgentRole.QA
            ],
            TaskScale.FEATURE: [
                AgentRole.ANALYST,
                AgentRole.DEV,
                AgentRole.QA,
                AgentRole.TECH_WRITER
            ],
            TaskScale.EPIC: [
                AgentRole.ANALYST,
                AgentRole.PM,
                AgentRole.ARCHITECT,
                AgentRole.UX,
                AgentRole.DEV,
                AgentRole.QA,
                AgentRole.TECH_WRITER
            ],
            TaskScale.ENTERPRISE: [
                AgentRole.ANALYST,
                AgentRole.PM,
                AgentRole.ARCHITECT,
                AgentRole.UX,
                AgentRole.DEV,
                AgentRole.QA,
                AgentRole.TECH_WRITER,
                AgentRole.SCRUM_MASTER,
                AgentRole.DEVOPS
            ]
        }

        return agents_map.get(scale, agents_map[TaskScale.FEATURE])

    def plan_execution(self, task: str) -> Dict[str, Any]:
        """
        Planifica la ejecucion de una tarea.

        Args:
            task: Descripcion de la tarea

        Returns:
            Plan de ejecucion completo
        """
        # Clasificar escala
        scale = self.classify_scale(task)

        # Obtener agentes y grafo
        agents = self.get_agents_for_scale(scale)
        graph = self.get_workflow_graph(scale)

        # Crear plan
        plan = {
            "task": task,
            "scale": scale.value,
            "agents": [a.value for a in agents],
            "workflow_graph": graph,
            "estimated_phases": len(set(graph.keys()) - {"start", "end"}),
            "created_at": datetime.now().isoformat(),
            "status": "planned"
        }

        # Guardar en estado
        self.state["pending_tasks"].append(plan)
        self._save_state()

        return plan

    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de orquestacion."""
        return {
            "current_phase": self.state["current_phase"],
            "active_agents": self.state["active_agents"],
            "pending_tasks": len(self.state["pending_tasks"]),
            "completed_tasks": len(self.state["completed_tasks"]),
            "available_agents": list(self.agents.keys())
        }

    def format_plan_output(self, plan: Dict[str, Any]) -> str:
        """Formatea el plan para output legible."""
        output = []
        output.append("## Plan de Ejecucion\n")
        output.append(f"**Tarea:** {plan['task']}")
        output.append(f"**Escala:** {plan['scale']}")
        output.append(f"**Fases estimadas:** {plan['estimated_phases']}")
        output.append(f"\n### Agentes Involucrados")
        for agent in plan['agents']:
            output.append(f"- {agent}")
        output.append(f"\n### Workflow")
        for node, nexts in plan['workflow_graph'].items():
            if node not in ['start', 'end']:
                output.append(f"- {node} -> {', '.join(nexts)}")
        return "\n".join(output)


def main():
    """Funcion principal CLI."""
    parser = argparse.ArgumentParser(
        description="NXT Multi-Agent Orchestrator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: plan
    plan_parser = subparsers.add_parser("plan", help="Planificar tarea")
    plan_parser.add_argument("task", help="Descripcion de la tarea")

    # Comando: status
    subparsers.add_parser("status", help="Ver estado actual")

    # Comando: classify
    classify_parser = subparsers.add_parser("classify", help="Clasificar escala de tarea")
    classify_parser.add_argument("task", help="Descripcion de la tarea")

    # Comando: delegate
    delegate_parser = subparsers.add_parser("delegate", help="Delegar tarea a agente")
    delegate_parser.add_argument("type", choices=[t.value for t in TaskType])
    delegate_parser.add_argument("--external", action="store_true")
    delegate_parser.add_argument("--non-technical", action="store_true")

    args = parser.parse_args()

    try:
        orchestrator = MultiAgentOrchestrator()

        if args.command == "plan":
            plan = orchestrator.plan_execution(args.task)
            print(orchestrator.format_plan_output(plan))

        elif args.command == "status":
            status = orchestrator.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))

        elif args.command == "classify":
            scale = orchestrator.classify_scale(args.task)
            print(json.dumps({"task": args.task, "scale": scale.value}, indent=2))

        elif args.command == "delegate":
            task_type = TaskType(args.type)
            agent = orchestrator.delegate(
                task_type,
                is_external=args.external,
                is_technical=not args.non_technical
            )
            print(json.dumps({"type": args.type, "agent": agent.value}, indent=2))

        else:
            parser.print_help()

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
