#!/usr/bin/env python3
"""
NXT AI Development - Orchestrator v3
=====================================
Implementación completa con:
- 5 niveles BMAD v6 Alpha (nivel_0 a nivel_4)
- LangGraph pattern para flujos como grafos
- Event-driven architecture
- Auto-delegación de agentes
- Carga dinámica de skills y workflows
- Integración MCP
- State sync continuo
- Self-Healing con circuit breaker
- Learning from decisions
- Self-Healing Manager integration (health, self-test CLI)

NOTA v3.8.0:
- Claude CLI externo ELIMINADO
- Los slash commands ahora usan "ejecución directa"
- Claude lee archivos de agentes y ejecuta con sus propias herramientas
- No requiere API keys ni subprocess
- Sincronización completa de versiones
- CI/CD con GitHub Actions
- Agentes de persistencia automáticos (context, multicontext, changelog, ralph)
- NUEVO: Fusión nxt-ux + nxt-uidev en nxt-design (Product Designer)
- NUEVO: Self-Healing Manager (health metrics, circuit breaker, self-test)

Versión: 3.8.0
Framework: 3.8.0
"""

import os
import sys
import json
import yaml
import argparse
import subprocess
import functools
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable, Set
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

# Importar utilidades locales
try:
    from utils import get_project_root, load_config, NXTContext
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from utils import get_project_root, load_config, NXTContext

# Importar Event Bus
try:
    from event_bus import EventBus, Event, EventType
except ImportError:
    EventBus = None
    Event = None
    EventType = None

# Self-Healing Manager (v3.8.0)
try:
    from self_healing import SelfHealingManager, InputSanitizer, DelegationGuard
    SELF_HEALING_AVAILABLE = True
except ImportError:
    SELF_HEALING_AVAILABLE = False
    SelfHealingManager = None

# NOTA: Claude CLI externo ya NO se usa (v3.4.0)
# Los slash commands ahora instruyen a Claude directamente
# sin necesidad de subprocess ni API keys externas
CLAUDE_CLI_AVAILABLE = False  # Deshabilitado - ejecución directa via slash commands


# =============================================================================
# ENUMS Y CONSTANTES - Sistema de 5 Niveles BMAD v6 Alpha
# =============================================================================

class TaskScale(Enum):
    """Escala de tarea según BMAD v6 Alpha - 5 Niveles."""
    NIVEL_0 = "nivel_0"  # Trivial: < 15min, instant track
    NIVEL_1 = "nivel_1"  # Simple: 15min-1h, quick_flow
    NIVEL_2 = "nivel_2"  # Estándar: 1-8h, bmad_method
    NIVEL_3 = "nivel_3"  # Complejo: 8-40h, full_planning
    NIVEL_4 = "nivel_4"  # Enterprise: 40h+, enterprise_track


# =============================================================================
# AGENTES DE PERSISTENCIA - SIEMPRE ACTIVOS (v3.5.1)
# =============================================================================
# Estos agentes se ejecutan AUTOMÁTICAMENTE en cada interacción para mantener
# el contexto, documentación y estado del proyecto siempre actualizado.

PERSISTENCE_AGENTS = [
    "nxt-context",       # Gestión de contexto entre sesiones
    "nxt-multicontext",  # Persistencia y recovery de estado
    "nxt-changelog",     # Documentación automática de cambios
    "nxt-ralph",         # Desarrollo autónomo iterativo (checkpoints)
]

# Triggers para ejecutar agentes de persistencia
# IMPORTANTE: "always" = CADA interacción del usuario debe ejecutar TODOS los agentes
PERSISTENCE_TRIGGERS = {
    "on_session_start": ["nxt-context", "nxt-multicontext"],  # Al iniciar sesión
    "on_task_complete": ["nxt-changelog", "nxt-context"],      # Al completar tarea
    "on_agent_switch": ["nxt-multicontext"],                   # Al cambiar agente
    "on_checkpoint": ["nxt-multicontext", "nxt-ralph"],        # Al crear checkpoint
    "on_session_end": ["nxt-context", "nxt-changelog"],        # Al terminar sesión
    # === TRIGGER PRINCIPAL (v3.5.1) ===
    # CADA mensaje del usuario activa TODOS los agentes de persistencia
    "always": ["nxt-context", "nxt-multicontext", "nxt-changelog", "nxt-ralph"],
    "on_every_interaction": ["nxt-context", "nxt-multicontext", "nxt-changelog", "nxt-ralph"],
}


class AgentRole(Enum):
    """Roles de agentes disponibles - 32 NXT + 12 BMAD."""
    # Core NXT Agents
    ORCHESTRATOR = "nxt-orchestrator"
    ANALYST = "nxt-analyst"
    PM = "nxt-pm"
    ARCHITECT = "nxt-architect"
    DESIGN = "nxt-design"  # v3.6.0: Fusion de UX + UIDEV
    DEV = "nxt-dev"
    QA = "nxt-qa"
    TECH_WRITER = "nxt-tech-writer"
    SCRUM_MASTER = "nxt-scrum-master"
    DEVOPS = "nxt-devops"

    # Extended NXT Agents (v3.1.0)
    CYBERSEC = "nxt-cybersec"
    API = "nxt-api"
    DATABASE = "nxt-database"
    INTEGRATIONS = "nxt-integrations"
    FLOWS = "nxt-flows"

    # Specialized NXT Agents (v3.1.0+)
    INFRA = "nxt-infra"
    MIGRATOR = "nxt-migrator"
    PERFORMANCE = "nxt-performance"
    ACCESSIBILITY = "nxt-accessibility"
    MOBILE = "nxt-mobile"
    DATA = "nxt-data"
    AIML = "nxt-aiml"
    COMPLIANCE = "nxt-compliance"
    REALTIME = "nxt-realtime"
    LOCALIZATION = "nxt-localization"

    # LLM Delegation Agents
    SEARCH = "nxt-search"
    MEDIA = "nxt-media"

    # Context & Automation Agents (v3.3.0)
    CONTEXT = "nxt-context"
    CHANGELOG = "nxt-changelog"
    RALPH = "nxt-ralph"
    MULTICONTEXT = "nxt-multicontext"

    # BMAD Paige Agent
    PAIGE = "nxt-paige"

    # Evaluation & Scoring (v3.8.0)
    SCORER = "nxt-scorer"
    EDGE_CASE_HUNTER = "nxt-edge-case-hunter"


class TaskType(Enum):
    """Tipos de tarea para delegación."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    DESIGN = "design"
    ARCHITECTURE = "architecture"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    DOCUMENTATION = "documentation"
    MULTIMEDIA = "multimedia"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    DATABASE = "database"
    INTEGRATION = "integration"
    # Extended types (v3.3.0)
    MIGRATION = "migration"
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    MOBILE = "mobile"
    DATA_ENGINEERING = "data_engineering"
    AI_ML = "ai_ml"
    COMPLIANCE = "compliance"
    REALTIME = "realtime"
    LOCALIZATION = "localization"
    CONTEXT_MANAGEMENT = "context_management"
    CHANGELOG = "changelog"
    AUTONOMOUS = "autonomous"
    HEALTH_EVALUATION = "health_evaluation"
    EDGE_CASE_REVIEW = "edge_case_review"


class WorkflowPhase(Enum):
    """Fases del workflow BMAD."""
    DISCOVER = "descubrir"
    DEFINE = "definir"
    DESIGN = "disenar"
    PLAN = "planificar"
    BUILD = "construir"
    VERIFY = "verificar"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class AgentInfo:
    """Información de un agente."""
    name: str
    file_path: str
    role: Optional[AgentRole] = None
    capabilities: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    phase: Optional[WorkflowPhase] = None
    is_bmad: bool = False
    active: bool = False


@dataclass
class SkillInfo:
    """Información de un skill."""
    name: str
    file_path: str
    category: str
    mcp_servers: List[str] = field(default_factory=list)
    agents: List[str] = field(default_factory=list)


@dataclass
class WorkflowInfo:
    """Información de un workflow."""
    name: str
    file_path: str
    phase: WorkflowPhase
    triggers: List[str] = field(default_factory=list)
    agents_required: List[str] = field(default_factory=list)
    is_bmad: bool = False


@dataclass
class ExecutionContext:
    """Contexto de ejecución actual."""
    task: str
    scale: TaskScale
    current_phase: WorkflowPhase
    current_agent: Optional[AgentRole] = None
    completed_steps: List[str] = field(default_factory=list)
    pending_steps: List[str] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# REGISTRIES - Carga Dinámica de Componentes
# =============================================================================

class AgentRegistry:
    """Registry unificado de agentes NXT + BMAD."""

    def __init__(self, root: Path):
        self.root = root
        self.agents: Dict[str, AgentInfo] = {}
        self._load_nxt_agents()
        self._load_bmad_agents()
        self._load_mapping()

    def _load_nxt_agents(self):
        """Carga agentes NXT desde agentes/."""
        agents_dir = self.root / "agentes"
        if agents_dir.exists():
            for agent_file in agents_dir.glob("nxt-*.md"):
                name = agent_file.stem
                self.agents[name] = AgentInfo(
                    name=name,
                    file_path=str(agent_file),
                    is_bmad=False
                )

    def _load_bmad_agents(self):
        """Carga agentes BMAD desde nxt/method/agents/."""
        bmad_dir = self.root / "nxt" / "method" / "agents"
        if bmad_dir.exists():
            for category_dir in bmad_dir.iterdir():
                if category_dir.is_dir():
                    for agent_file in category_dir.glob("*.agent.md"):
                        name = f"bmad-{agent_file.stem.replace('.agent', '')}"
                        self.agents[name] = AgentInfo(
                            name=name,
                            file_path=str(agent_file),
                            is_bmad=True
                        )

    def _load_mapping(self):
        """Carga mapeo BMAD→NXT si existe."""
        mapping_file = self.root / ".nxt" / "bmad-nxt-mapping.yaml"
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping = yaml.safe_load(f)
                if mapping and 'agent_mapping' in mapping:
                    for bmad_name, nxt_name in mapping['agent_mapping'].items():
                        if bmad_name in self.agents:
                            self.agents[bmad_name].capabilities.append(f"maps_to:{nxt_name}")

    def get(self, name: str) -> Optional[AgentInfo]:
        """Obtiene un agente por nombre."""
        return self.agents.get(name)

    def get_by_role(self, role: AgentRole) -> Optional[AgentInfo]:
        """Obtiene un agente por rol."""
        return self.agents.get(role.value)

    def list_all(self) -> List[AgentInfo]:
        """Lista todos los agentes."""
        return list(self.agents.values())

    def list_nxt(self) -> List[AgentInfo]:
        """Lista solo agentes NXT."""
        return [a for a in self.agents.values() if not a.is_bmad]

    def list_bmad(self) -> List[AgentInfo]:
        """Lista solo agentes BMAD."""
        return [a for a in self.agents.values() if a.is_bmad]


class SkillRegistry:
    """Registry de skills con carga dinámica."""

    def __init__(self, root: Path):
        self.root = root
        self.skills: Dict[str, SkillInfo] = {}
        self._load_skills()
        self._load_mcp_mapping()

    def _load_skills(self):
        """Carga skills desde skills/."""
        skills_dir = self.root / "skills"
        if skills_dir.exists():
            for category_dir in skills_dir.iterdir():
                if category_dir.is_dir():
                    category = category_dir.name
                    for skill_file in category_dir.glob("SKILL-*.md"):
                        name = skill_file.stem.replace("SKILL-", "")
                        self.skills[name] = SkillInfo(
                            name=name,
                            file_path=str(skill_file),
                            category=category
                        )

    def _load_mcp_mapping(self):
        """Carga mapeo skill→MCP si existe."""
        mapping_file = self.root / ".nxt" / "skill-mcp-mapping.yaml"
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                mapping = yaml.safe_load(f)
                if mapping and 'skill_mcp' in mapping:
                    for skill_name, mcp_servers in mapping['skill_mcp'].items():
                        if skill_name in self.skills:
                            self.skills[skill_name].mcp_servers = mcp_servers

    def get(self, name: str) -> Optional[SkillInfo]:
        """Obtiene un skill por nombre."""
        return self.skills.get(name)

    def get_by_category(self, category: str) -> List[SkillInfo]:
        """Obtiene skills por categoría."""
        return [s for s in self.skills.values() if s.category == category]

    def list_all(self) -> List[SkillInfo]:
        """Lista todos los skills."""
        return list(self.skills.values())

    def get_for_agent(self, agent_name: str) -> List[SkillInfo]:
        """Obtiene skills asignados a un agente."""
        return [s for s in self.skills.values() if agent_name in s.agents]


class WorkflowRegistry:
    """Registry de workflows BMAD + NXT."""

    def __init__(self, root: Path):
        self.root = root
        self.workflows: Dict[str, WorkflowInfo] = {}
        self._load_bmad_workflows()
        self._load_nxt_workflows()

    def _load_bmad_workflows(self):
        """Carga workflows BMAD desde nxt/method/workflows/."""
        workflows_dir = self.root / "nxt" / "method" / "workflows"
        if workflows_dir.exists():
            phase_mapping = {
                "1-discovery": WorkflowPhase.DISCOVER,
                "2-planning": WorkflowPhase.DEFINE,
                "3-solutioning": WorkflowPhase.DESIGN,
                "4-delivery": WorkflowPhase.BUILD,
            }
            for phase_dir in workflows_dir.iterdir():
                if phase_dir.is_dir():
                    phase = phase_mapping.get(phase_dir.name, WorkflowPhase.BUILD)
                    for wf_dir in phase_dir.iterdir():
                        if wf_dir.is_dir():
                            workflow_file = wf_dir / "workflow.yaml"
                            if workflow_file.exists():
                                name = f"bmad-{wf_dir.name}"
                                self.workflows[name] = WorkflowInfo(
                                    name=name,
                                    file_path=str(workflow_file),
                                    phase=phase,
                                    is_bmad=True
                                )

    def _load_nxt_workflows(self):
        """Carga workflows NXT desde workflows/."""
        workflows_dir = self.root / "workflows"
        if workflows_dir.exists():
            phase_mapping = {
                "fase-1": WorkflowPhase.DISCOVER,
                "fase-2": WorkflowPhase.DEFINE,
                "fase-3": WorkflowPhase.DESIGN,
                "fase-4": WorkflowPhase.PLAN,
                "fase-5": WorkflowPhase.BUILD,
                "fase-6": WorkflowPhase.VERIFY,
            }
            for item in workflows_dir.iterdir():
                if item.is_dir():
                    for key, phase in phase_mapping.items():
                        if key in item.name:
                            for wf_file in item.glob("*.md"):
                                name = wf_file.stem
                                self.workflows[name] = WorkflowInfo(
                                    name=name,
                                    file_path=str(wf_file),
                                    phase=phase,
                                    is_bmad=False
                                )
                            break
                elif item.suffix == ".md":
                    name = item.stem
                    self.workflows[name] = WorkflowInfo(
                        name=name,
                        file_path=str(item),
                        phase=WorkflowPhase.BUILD,
                        is_bmad=False
                    )

    def get(self, name: str) -> Optional[WorkflowInfo]:
        """Obtiene un workflow por nombre."""
        return self.workflows.get(name)

    def get_by_phase(self, phase: WorkflowPhase) -> List[WorkflowInfo]:
        """Obtiene workflows por fase."""
        return [w for w in self.workflows.values() if w.phase == phase]

    def list_all(self) -> List[WorkflowInfo]:
        """Lista todos los workflows."""
        return list(self.workflows.values())


# =============================================================================
# CLASSIFIER - Sistema de 5 Niveles BMAD v6 Alpha
# =============================================================================

class TaskClassifier:
    """Clasificador de tareas en 5 niveles BMAD v6 Alpha."""

    # Keywords por nivel
    KEYWORDS = {
        TaskScale.NIVEL_0: [
            "typo", "fix typo", "comment", "readme", "docs fix",
            "whitespace", "formatting", "lint", "style fix"
        ],
        TaskScale.NIVEL_1: [
            "bug", "fix", "hotfix", "patch", "error", "issue",
            "small feature", "minor", "quick", "simple"
        ],
        TaskScale.NIVEL_2: [
            "feature", "implement", "add", "create", "new",
            "update", "modify", "enhance", "improve"
        ],
        TaskScale.NIVEL_3: [
            "refactor", "redesign", "module", "system", "epic",
            "authentication", "authorization", "migration", "upgrade"
        ],
        TaskScale.NIVEL_4: [
            "architecture", "platform", "infrastructure", "microservices",
            "enterprise", "scalability", "multi-tenant", "distributed"
        ]
    }

    # Configuración por nivel
    LEVEL_CONFIG = {
        TaskScale.NIVEL_0: {
            "max_files": 2,
            "max_hours": 0.25,
            "track": "instant",
            "agents": [AgentRole.DEV]
        },
        TaskScale.NIVEL_1: {
            "max_files": 5,
            "max_hours": 1,
            "track": "quick_flow",
            "agents": [AgentRole.DEV, AgentRole.QA]
        },
        TaskScale.NIVEL_2: {
            "max_files": 15,
            "max_hours": 8,
            "track": "bmad_method",
            "agents": [AgentRole.ANALYST, AgentRole.DEV, AgentRole.QA, AgentRole.TECH_WRITER]
        },
        TaskScale.NIVEL_3: {
            "max_files": 50,
            "max_hours": 40,
            "track": "full_planning",
            "agents": [
                AgentRole.ANALYST, AgentRole.PM, AgentRole.ARCHITECT,
                AgentRole.DESIGN, AgentRole.DEV, AgentRole.QA, AgentRole.TECH_WRITER
            ]
        },
        TaskScale.NIVEL_4: {
            "max_files": 999,
            "max_hours": 999,
            "track": "enterprise_track",
            "agents": [
                AgentRole.ANALYST, AgentRole.PM, AgentRole.ARCHITECT,
                AgentRole.DESIGN, AgentRole.DEV, AgentRole.QA, AgentRole.TECH_WRITER,
                AgentRole.SCRUM_MASTER, AgentRole.DEVOPS, AgentRole.CYBERSEC
            ]
        }
    }

    @staticmethod
    @functools.lru_cache(maxsize=256)
    def _match_keywords(task_lower: str) -> Optional[TaskScale]:
        """Cached keyword matching - avoids re-scanning keywords for repeated tasks."""
        for level in [TaskScale.NIVEL_4, TaskScale.NIVEL_3,
                      TaskScale.NIVEL_2, TaskScale.NIVEL_1, TaskScale.NIVEL_0]:
            if any(kw in task_lower for kw in TaskClassifier.KEYWORDS[level]):
                return level
        return None

    @classmethod
    def classify(cls, task: str, estimated_files: int = 0,
                 estimated_hours: float = 0) -> TaskScale:
        """
        Clasifica una tarea en uno de los 5 niveles BMAD.

        Args:
            task: Descripción de la tarea
            estimated_files: Número estimado de archivos
            estimated_hours: Horas estimadas

        Returns:
            TaskScale correspondiente
        """
        task_lower = task.lower()

        # Primero verificar por keywords (cached para tareas repetidas)
        keyword_level = cls._match_keywords(task_lower)
        if keyword_level is not None:
            # Si es nivel alto pero estimaciones son bajas, ajustar
            if keyword_level in [TaskScale.NIVEL_3, TaskScale.NIVEL_4]:
                if estimated_hours > 0 and estimated_hours < 8:
                    # Fallback: buscar nivel más bajo
                    for level in [TaskScale.NIVEL_2, TaskScale.NIVEL_1, TaskScale.NIVEL_0]:
                        if any(kw in task_lower for kw in cls.KEYWORDS[level]):
                            return level
                else:
                    return keyword_level
            else:
                return keyword_level

        # Clasificar por métricas si no hay keywords claros
        if estimated_hours > 40 or estimated_files > 50:
            return TaskScale.NIVEL_4
        elif estimated_hours > 8 or estimated_files > 15:
            return TaskScale.NIVEL_3
        elif estimated_hours > 1 or estimated_files > 5:
            return TaskScale.NIVEL_2
        elif estimated_hours > 0.25 or estimated_files > 2:
            return TaskScale.NIVEL_1

        # Default a nivel 2 (estándar) para tareas ambiguas
        return TaskScale.NIVEL_2

    @classmethod
    def get_config(cls, scale: TaskScale) -> Dict[str, Any]:
        """Obtiene la configuración para un nivel."""
        return cls.LEVEL_CONFIG[scale]

    @classmethod
    def get_agents(cls, scale: TaskScale) -> List[AgentRole]:
        """Obtiene los agentes requeridos para un nivel."""
        return cls.LEVEL_CONFIG[scale]["agents"]

    @classmethod
    def get_track(cls, scale: TaskScale) -> str:
        """Obtiene el track de workflow para un nivel."""
        return cls.LEVEL_CONFIG[scale]["track"]


# =============================================================================
# DELEGATOR - Sistema de Delegación Inteligente
# =============================================================================

class AgentDelegator:
    """Sistema de delegación inteligente de tareas a agentes."""

    # Mapeo de tipos de tarea a agentes
    DELEGATION_MAP = {
        TaskType.RESEARCH: {
            "external": AgentRole.SEARCH,
            "internal": AgentRole.ANALYST
        },
        TaskType.ANALYSIS: {
            "default": AgentRole.ANALYST
        },
        TaskType.DESIGN: {
            "default": AgentRole.DESIGN,  # v3.6.0: DESIGN por defecto
            "technical": AgentRole.ARCHITECT,
            "user": AgentRole.DESIGN,  # v3.6.0: DESIGN reemplaza UX
            "ui": AgentRole.DESIGN,    # v3.6.0: DESIGN reemplaza UIDEV
            "ux": AgentRole.DESIGN     # v3.6.0: DESIGN maneja todo
        },
        TaskType.ARCHITECTURE: {
            "default": AgentRole.ARCHITECT
        },
        TaskType.IMPLEMENTATION: {
            "default": AgentRole.DEV,  # v3.6.0: DEV por defecto
            "frontend": AgentRole.DESIGN,  # v3.6.0: DESIGN hace frontend UI
            "backend": AgentRole.API,
            "fullstack": AgentRole.DEV
        },
        TaskType.VALIDATION: {
            "default": AgentRole.QA
        },
        TaskType.DOCUMENTATION: {
            "default": AgentRole.TECH_WRITER
        },
        TaskType.MULTIMEDIA: {
            "default": AgentRole.MEDIA
        },
        TaskType.INFRASTRUCTURE: {
            "cicd": AgentRole.DEVOPS,
            "cloud": AgentRole.INFRA,
            "kubernetes": AgentRole.INFRA,
            "k8s": AgentRole.INFRA,
            "terraform": AgentRole.INFRA,
            "helm": AgentRole.INFRA,
            "iac": AgentRole.INFRA,
            "aws": AgentRole.INFRA,
            "gcp": AgentRole.INFRA,
            "azure": AgentRole.INFRA,
            "docker": AgentRole.DEVOPS,
            "github_actions": AgentRole.DEVOPS,
            "gitlab_ci": AgentRole.DEVOPS,
            "pipeline": AgentRole.DEVOPS,
            "default": AgentRole.DEVOPS
        },
        TaskType.SECURITY: {
            "oauth": AgentRole.CYBERSEC,
            "auth": AgentRole.CYBERSEC,
            "owasp": AgentRole.CYBERSEC,
            "default": AgentRole.CYBERSEC
        },
        TaskType.DATABASE: {
            "default": AgentRole.DATABASE
        },
        TaskType.INTEGRATION: {
            "default": AgentRole.INTEGRATIONS
        },
        # Extended mappings (v3.3.0)
        TaskType.MIGRATION: {
            "default": AgentRole.MIGRATOR
        },
        TaskType.PERFORMANCE: {
            "default": AgentRole.PERFORMANCE
        },
        TaskType.ACCESSIBILITY: {
            "default": AgentRole.ACCESSIBILITY
        },
        TaskType.MOBILE: {
            "default": AgentRole.MOBILE
        },
        TaskType.DATA_ENGINEERING: {
            "default": AgentRole.DATA
        },
        TaskType.AI_ML: {
            "default": AgentRole.AIML
        },
        TaskType.COMPLIANCE: {
            "default": AgentRole.COMPLIANCE
        },
        TaskType.REALTIME: {
            "default": AgentRole.REALTIME
        },
        TaskType.LOCALIZATION: {
            "default": AgentRole.LOCALIZATION
        },
        TaskType.CONTEXT_MANAGEMENT: {
            "session": AgentRole.CONTEXT,
            "persistence": AgentRole.MULTICONTEXT,
            "default": AgentRole.CONTEXT
        },
        TaskType.CHANGELOG: {
            "default": AgentRole.CHANGELOG
        },
        TaskType.AUTONOMOUS: {
            "default": AgentRole.RALPH
        },
        # Evaluation & Scoring (v3.8.0)
        TaskType.HEALTH_EVALUATION: {
            "default": AgentRole.SCORER,
            "quick": AgentRole.SCORER,
            "full": AgentRole.SCORER
        },
        TaskType.EDGE_CASE_REVIEW: {
            "default": AgentRole.EDGE_CASE_HUNTER
        }
    }

    @classmethod
    def delegate(cls, task_type: TaskType,
                 variant: str = "default") -> AgentRole:
        """
        Delega una tarea al agente apropiado.

        Args:
            task_type: Tipo de tarea
            variant: Variante específica (external/internal, technical/user, etc.)

        Returns:
            AgentRole del agente delegado
        """
        type_map = cls.DELEGATION_MAP.get(task_type, {})

        # Buscar variante específica o default
        if variant in type_map:
            return type_map[variant]
        elif "default" in type_map:
            return type_map["default"]

        # Fallback a PM para coordinar
        return AgentRole.PM

    @classmethod
    def infer_task_type(cls, task: str) -> TaskType:
        """
        Infiere el tipo de tarea desde la descripción.

        Args:
            task: Descripción de la tarea

        Returns:
            TaskType inferido
        """
        task_lower = task.lower()

        # IMPORTANTE: El orden importa. Los tipos más específicos deben ir primero
        # para evitar que keywords genéricas capturen tareas específicas.
        keywords_map = {
            # === PERSISTENCIA (v3.5.1) - Evaluar PRIMERO ===
            TaskType.AUTONOMOUS: ["autonomous", "ralph", "ralph loop", "iterate until", "auto-fix", "autonomo", "iterativo autonomo"],
            TaskType.CONTEXT_MANAGEMENT: ["context", "checkpoint", "recovery", "session state", "contexto", "guardar estado", "cargar contexto", "persistir"],
            TaskType.CHANGELOG: ["changelog", "release notes", "what changed", "cambios de version", "historial de cambios"],

            # === TIPOS ESPECÍFICOS ===
            TaskType.MIGRATION: ["migrate", "migration", "upgrade version", "modernize", "migrar codigo", "legacy system"],
            TaskType.PERFORMANCE: ["performance", "optimize", "profiling", "web vitals", "speed", "rendimiento", "lento"],
            TaskType.ACCESSIBILITY: ["accessibility", "a11y", "wcag", "aria", "screen reader", "accesibilidad"],
            TaskType.MOBILE: ["mobile app", "react native", "flutter", "ios app", "android app", "pwa"],
            TaskType.DATA_ENGINEERING: ["etl", "airflow", "data pipeline", "data warehouse", "dbt", "spark"],
            TaskType.AI_ML: ["machine learning", "ml model", "ai model", "training", "llm", "rag"],
            TaskType.COMPLIANCE: ["compliance", "gdpr", "hipaa", "soc2", "audit", "privacy", "cumplimiento"],
            TaskType.REALTIME: ["realtime", "websocket", "sse", "streaming", "presence", "tiempo real"],
            TaskType.LOCALIZATION: ["localization", "i18n", "l10n", "translation", "rtl", "traduccion"],

            # === TIPOS GENERALES ===
            TaskType.RESEARCH: ["research", "investigate", "search for", "find info", "look for", "buscar info"],
            TaskType.ANALYSIS: ["analyze", "analyse", "review code", "assess", "analizar"],
            TaskType.DESIGN: ["design ui", "wireframe", "mockup", "prototype", "ux design", "disenar interfaz", "diseno de interfaz", "user interface", "experiencia de usuario", "flujo de usuario", "user flow"],
            TaskType.ARCHITECTURE: ["architecture", "system design", "structure", "arquitectura"],
            TaskType.SECURITY: ["security", "vulnerability", "owasp", "seguridad", "penetration test"],
            TaskType.DATABASE: ["database", "sql query", "schema", "base de datos", "postgres", "mongodb"],
            TaskType.INTEGRATION: ["integrate", "api integration", "webhook", "connect service", "third-party"],
            TaskType.INFRASTRUCTURE: ["deploy", "ci/cd", "docker", "kubernetes", "infra", "terraform", "helm"],
            TaskType.VALIDATION: ["test", "validate", "verify", "qa", "quality", "probar"],
            TaskType.DOCUMENTATION: ["document", "docs", "readme", "guide", "documentar"],
            TaskType.MULTIMEDIA: ["image", "video", "audio", "media", "imagen"],

            # === IMPLEMENTACIÓN (fallback antes del default) ===
            TaskType.IMPLEMENTATION: ["implement", "code", "develop", "build", "crear", "programar"],
        }

        for task_type, keywords in keywords_map.items():
            if any(kw in task_lower for kw in keywords):
                return task_type

        # Default a implementación
        return TaskType.IMPLEMENTATION


# =============================================================================
# WORKFLOW GRAPH - LangGraph Pattern
# =============================================================================

class WorkflowGraph:
    """Generador de grafos de workflow estilo LangGraph."""

    # Grafos predefinidos por nivel
    GRAPHS = {
        TaskScale.NIVEL_0: {
            "start": ["dev"],
            "dev": ["end"]
        },
        TaskScale.NIVEL_1: {
            "start": ["dev"],
            "dev": ["qa"],
            "qa": ["end"]
        },
        TaskScale.NIVEL_2: {
            "start": ["analyst"],
            "analyst": ["dev"],
            "dev": ["qa"],
            "qa": ["docs"],
            "docs": ["end"]
        },
        TaskScale.NIVEL_3: {
            "start": ["analyst"],
            "analyst": ["pm"],
            "pm": ["architect", "design"],
            "architect": ["dev"],
            "design": ["dev"],  # v3.6.0: design reemplaza ux+uidev
            "dev": ["qa"],
            "qa": ["docs"],
            "docs": ["review"],
            "review": ["end"]
        },
        TaskScale.NIVEL_4: {
            "start": ["analyst"],
            "analyst": ["pm"],
            "pm": ["architect", "design", "cybersec"],
            "architect": ["dev", "devops"],
            "design": ["dev"],  # v3.6.0: design hace UX+UI completo
            "cybersec": ["dev"],
            "devops": ["dev"],
            "dev": ["qa"],
            "qa": ["docs", "devops_deploy"],
            "docs": ["review"],
            "devops_deploy": ["review"],
            "review": ["end"]
        }
    }

    # Mapeo de nodos a agentes
    NODE_TO_AGENT = {
        "analyst": AgentRole.ANALYST,
        "pm": AgentRole.PM,
        "architect": AgentRole.ARCHITECT,
        "design": AgentRole.DESIGN,  # v3.6.0: reemplaza ux y uidev
        "dev": AgentRole.DEV,
        "qa": AgentRole.QA,
        "docs": AgentRole.TECH_WRITER,
        "devops": AgentRole.DEVOPS,
        "devops_deploy": AgentRole.DEVOPS,
        "cybersec": AgentRole.CYBERSEC,
        "review": AgentRole.PM,
    }

    @classmethod
    def get_graph(cls, scale: TaskScale) -> Dict[str, List[str]]:
        """Obtiene el grafo de workflow para un nivel."""
        return cls.GRAPHS.get(scale, cls.GRAPHS[TaskScale.NIVEL_2])

    @classmethod
    def get_agent_for_node(cls, node: str) -> Optional[AgentRole]:
        """Obtiene el agente para un nodo del grafo."""
        return cls.NODE_TO_AGENT.get(node)

    @classmethod
    def get_next_nodes(cls, graph: Dict[str, List[str]],
                       current: str) -> List[str]:
        """Obtiene los nodos siguientes desde el nodo actual."""
        return graph.get(current, [])

    @classmethod
    def get_execution_order(cls, scale: TaskScale) -> List[str]:
        """
        Obtiene el orden de ejecución linealizado del grafo.
        Para grafos con paralelismo, agrupa los nodos paralelos.
        """
        graph = cls.get_graph(scale)
        order = []
        visited = set()
        queue = ["start"]

        while queue:
            current = queue.pop(0)
            if current in visited or current == "end":
                continue

            if current != "start":
                order.append(current)

            visited.add(current)
            next_nodes = graph.get(current, [])
            queue.extend([n for n in next_nodes if n not in visited])

        return order


# =============================================================================
# STATE MANAGER - Persistencia y Sincronización
# =============================================================================

class StateManager:
    """Gestor de estado persistente con sincronización."""

    def __init__(self, root: Path):
        self.root = root
        self.state_file = root / ".nxt" / "state.json"
        self.decisions_file = root / ".nxt" / "decisions.log"
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Carga el estado desde archivo con validación de proyecto."""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            # Multi-project safety: validate project identity
            state_project = state.get("project_path", "")
            current_project = self.root.name
            if state_project and state_project != current_project:
                import sys
                print(f"WARNING: state.json belongs to '{state_project}' but "
                      f"current project is '{current_project}'. Using default state.",
                      file=sys.stderr)
                return self._default_state()
            return state
        return self._default_state()

    def _default_state(self) -> Dict[str, Any]:
        """Estado por defecto."""
        return {
            "framework_version": "3.8.0",
            "current_phase": "init",
            "current_context": None,
            "completed_tasks": [],
            "pending_tasks": [],
            "active_agents": [],
            "decisions_log": [],
            "session_history": [],
            "last_updated": datetime.now().isoformat()
        }

    def save(self):
        """Guarda el estado a archivo."""
        self.state["last_updated"] = datetime.now().isoformat()
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def update(self, **kwargs):
        """Actualiza campos del estado."""
        self.state.update(kwargs)
        self.save()

    def log_decision(self, decision: Dict[str, Any]):
        """Registra una decisión."""
        decision["timestamp"] = datetime.now().isoformat()
        self.state["decisions_log"].append(decision)
        self.save()

        # También escribir a archivo de log
        self.decisions_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.decisions_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(decision, ensure_ascii=False) + "\n")

    def add_pending_task(self, task: Dict[str, Any]):
        """Agrega una tarea pendiente (sin duplicados)."""
        # Evitar duplicados por task name + scale
        task_name = task.get("task", "")
        for existing in self.state["pending_tasks"]:
            if existing.get("task") == task_name and existing.get("scale") == task.get("scale"):
                return  # Ya existe, no duplicar
        self.state["pending_tasks"].append(task)
        self.save()

    def complete_task(self, task_id: str):
        """Marca una tarea como completada."""
        for i, task in enumerate(self.state["pending_tasks"]):
            if task.get("id") == task_id or task.get("task") == task_id:
                completed = self.state["pending_tasks"].pop(i)
                completed["completed_at"] = datetime.now().isoformat()
                self.state["completed_tasks"].append(completed)
                self.save()
                return completed
        return None

    def update_agent_status(self, plan_id: str, agent: str, status: str):
        """Update execution status of an agent in a plan."""
        for task in self.state.get("pending_tasks", []):
            if task.get("id") == plan_id:
                if "execution_status" not in task:
                    task["execution_status"] = {}
                task["execution_status"][agent] = status
                self.save()
                return True
        return False

    def set_active_agent(self, agent: str):
        """Establece el agente activo."""
        if agent not in self.state["active_agents"]:
            self.state["active_agents"].append(agent)
            self.save()

    def clear_active_agents(self):
        """Limpia los agentes activos."""
        self.state["active_agents"] = []
        self.save()

    def get_context(self) -> Optional[ExecutionContext]:
        """Obtiene el contexto de ejecución actual."""
        ctx_data = self.state.get("current_context")
        if ctx_data:
            # Convertir strings a Enums
            scale_str = ctx_data.get("scale")
            phase_str = ctx_data.get("current_phase")
            agent_str = ctx_data.get("current_agent")

            return ExecutionContext(
                task=ctx_data.get("task", ""),
                scale=TaskScale(scale_str) if scale_str else TaskScale.NIVEL_2,
                current_phase=WorkflowPhase(phase_str) if phase_str else WorkflowPhase.DISCOVER,
                current_agent=AgentRole(agent_str) if agent_str else None,
                completed_steps=ctx_data.get("completed_steps", []),
                pending_steps=ctx_data.get("pending_steps", []),
                artifacts=ctx_data.get("artifacts", {}),
                decisions=ctx_data.get("decisions", []),
                started_at=ctx_data.get("started_at", "")
            )
        return None

    def set_context(self, context: ExecutionContext):
        """Establece el contexto de ejecución."""
        self.state["current_context"] = {
            "task": context.task,
            "scale": context.scale.value,
            "current_phase": context.current_phase.value,
            "current_agent": context.current_agent.value if context.current_agent else None,
            "completed_steps": context.completed_steps,
            "pending_steps": context.pending_steps,
            "artifacts": context.artifacts,
            "decisions": context.decisions,
            "started_at": context.started_at
        }

    # =========================================================================
    # LEARNING CAPABILITIES
    # =========================================================================

    def learn_from_decisions(self) -> Dict[str, Any]:
        """
        Analiza decisiones pasadas para aprender patrones.

        Returns:
            Insights aprendidos del historial
        """
        decisions = self.state.get("decisions_log", [])
        if not decisions:
            return {"patterns": [], "recommendations": []}

        # Análisis de clasificaciones
        classifications = [d for d in decisions if d.get("type") == "classification"]
        scale_counts = {}
        for c in classifications:
            scale = c.get("scale", "unknown")
            scale_counts[scale] = scale_counts.get(scale, 0) + 1

        # Análisis de delegaciones
        delegations = [d for d in decisions if d.get("type") == "delegation"]
        agent_counts = {}
        for d in delegations:
            agent = d.get("agent", "unknown")
            agent_counts[agent] = agent_counts.get(agent, 0) + 1

        # Identificar patrones
        patterns = []
        if scale_counts:
            most_common_scale = max(scale_counts, key=scale_counts.get)
            patterns.append(f"Most common scale: {most_common_scale}")

        if agent_counts:
            most_used_agent = max(agent_counts, key=agent_counts.get)
            patterns.append(f"Most used agent: {most_used_agent}")

        # Generar recomendaciones
        recommendations = []
        if len(classifications) > 10:
            if scale_counts.get("nivel_0", 0) > len(classifications) * 0.5:
                recommendations.append("Consider batching trivial tasks")
            if scale_counts.get("nivel_4", 0) > len(classifications) * 0.3:
                recommendations.append("High complexity projects - ensure architect involvement")

        return {
            "total_decisions": len(decisions),
            "scale_distribution": scale_counts,
            "agent_usage": agent_counts,
            "patterns": patterns,
            "recommendations": recommendations
        }

    def get_similar_decisions(self, task: str, limit: int = 5) -> List[Dict]:
        """
        Busca decisiones similares pasadas.

        Args:
            task: Descripción de la tarea
            limit: Número máximo de resultados

        Returns:
            Lista de decisiones similares
        """
        decisions = self.state.get("decisions_log", [])

        # Palabras clave de la tarea
        task_words = set(task.lower().split())

        # Buscar similares
        similar = []
        for d in decisions:
            d_task = d.get("task", "")
            d_words = set(d_task.lower().split())

            # Calcular similitud simple (Jaccard)
            if d_words:
                intersection = len(task_words & d_words)
                union = len(task_words | d_words)
                similarity = intersection / union if union > 0 else 0

                if similarity > 0.2:  # Umbral mínimo
                    similar.append({**d, "similarity": round(similarity, 2)})

        # Ordenar por similitud y limitar
        similar.sort(key=lambda x: x["similarity"], reverse=True)
        return similar[:limit]

    def predict_classification(self, task: str) -> Optional[str]:
        """
        Predice la clasificación basada en tareas similares.

        Args:
            task: Descripción de la tarea

        Returns:
            Clasificación predicha o None
        """
        similar = self.get_similar_decisions(task, limit=10)
        similar_classifications = [
            s for s in similar
            if s.get("type") == "classification" and s.get("similarity", 0) > 0.3
        ]

        if not similar_classifications:
            return None

        # Votar por la clasificación más común
        scale_votes = {}
        for s in similar_classifications:
            scale = s.get("scale")
            weight = s.get("similarity", 1)
            scale_votes[scale] = scale_votes.get(scale, 0) + weight

        if scale_votes:
            return max(scale_votes, key=scale_votes.get)
        return None


# =============================================================================
# HOOK MANAGER - Sistema de Hooks
# =============================================================================

class HookManager:
    """Gestor de hooks para eventos del sistema."""

    def __init__(self, root: Path):
        self.root = root
        self.hooks_dir = root / "plugins" / "nxt-core" / "hooks"
        self.hooks: Dict[str, Path] = {}
        self._load_hooks()

    def _load_hooks(self):
        """Carga hooks disponibles."""
        if self.hooks_dir.exists():
            for hook_file in self.hooks_dir.glob("*.sh"):
                hook_name = hook_file.stem.replace("-", "_")
                self.hooks[hook_name] = hook_file
            for hook_file in self.hooks_dir.glob("*.py"):
                hook_name = hook_file.stem.replace("-", "_")
                self.hooks[hook_name] = hook_file

    def execute(self, hook_name: str, context: Dict[str, Any] = None) -> bool:
        """
        Ejecuta un hook si existe.

        Args:
            hook_name: Nombre del hook (on_init, on_agent_switch, etc.)
            context: Contexto a pasar al hook

        Returns:
            True si se ejecutó exitosamente
        """
        hook_file = self.hooks.get(hook_name)
        if not hook_file or not hook_file.exists():
            return False

        try:
            env = os.environ.copy()
            if context:
                env["NXT_HOOK_CONTEXT"] = json.dumps(context)

            if hook_file.suffix == ".sh":
                subprocess.run(["bash", str(hook_file)],
                             env=env, capture_output=True, timeout=30)
            elif hook_file.suffix == ".py":
                subprocess.run([sys.executable, str(hook_file)],
                             env=env, capture_output=True, timeout=30)
            return True
        except Exception:
            return False

    def has_hook(self, hook_name: str) -> bool:
        """Verifica si existe un hook."""
        return hook_name in self.hooks


# =============================================================================
# ORCHESTRATOR V3 - Clase Principal
# =============================================================================

class NXTOrchestratorV3:
    """
    Orquestador NXT v3 - Integración Total.

    Características:
    - 5 niveles BMAD v6 Alpha
    - Carga dinámica de agentes, skills, workflows
    - Event-driven architecture
    - Auto-delegación inteligente
    - State sync continuo
    - Hooks system
    """

    def __init__(self):
        """
        Inicializa el orquestador.

        NOTA v3.4.0: Claude CLI externo ya no se usa.
        La ejecución de agentes se realiza directamente via slash commands.
        """
        self.root = get_project_root()
        self.config = load_config()

        # Inicializar componentes
        self.state_manager = StateManager(self.root)
        self.hook_manager = HookManager(self.root)

        # Registries
        self.agents = AgentRegistry(self.root)
        self.skills = SkillRegistry(self.root)
        self.workflows = WorkflowRegistry(self.root)

        # Event Bus (si está disponible)
        self.event_bus = EventBus() if EventBus else None

        # Ejecutar hook de inicialización
        self.hook_manager.execute("on_init", {
            "version": "3.8.0",
            "agents_count": len(self.agents.list_all()),
            "skills_count": len(self.skills.list_all()),
            "workflows_count": len(self.workflows.list_all()),
            "execution_mode": "direct"  # Ejecución directa via slash commands
        })

    def classify(self, task: str, estimated_files: int = 0,
                 estimated_hours: float = 0) -> TaskScale:
        """
        Clasifica una tarea usando el sistema de 5 niveles BMAD.

        Args:
            task: Descripción de la tarea
            estimated_files: Archivos estimados a modificar
            estimated_hours: Horas estimadas de trabajo

        Returns:
            TaskScale (nivel_0 a nivel_4)
        """
        # Sanitize input if available
        if SELF_HEALING_AVAILABLE:
            task = InputSanitizer.sanitize_task(task)

        scale = TaskClassifier.classify(task, estimated_files, estimated_hours)

        # Registrar decisión
        self.state_manager.log_decision({
            "type": "classification",
            "task": task,
            "scale": scale.value,
            "estimated_files": estimated_files,
            "estimated_hours": estimated_hours
        })

        # Emitir evento de clasificación
        if self.event_bus and EventType:
            self.event_bus.emit(EventType.TASK_CLASSIFIED, {
                "task": task,
                "scale": scale.value,
                "estimated_files": estimated_files,
                "estimated_hours": estimated_hours
            }, source="orchestrator")

        return scale

    def _load_scores(self) -> Optional[Dict[str, Any]]:
        """
        Carga .nxt/scores.json para score-aware planning.
        Returns None si no hay scores disponibles.
        """
        try:
            scores_path = self.root / ".nxt" / "scores.json"
            if scores_path.exists():
                with open(scores_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None

    def _load_capabilities(self) -> Dict[str, Any]:
        """
        Carga capabilities.yaml para validar delegaciones.
        Retorna dict vacío si no se puede cargar (graceful degradation).
        """
        try:
            caps_path = self.root / ".nxt" / "capabilities.yaml"
            if caps_path.exists():
                with open(caps_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        except Exception:
            pass
        return {}

    def _validate_agent_capability(self, agent: AgentRole, task_type: TaskType) -> bool:
        """
        Verifica que el agente tenga la capacidad requerida según capabilities.yaml.

        Args:
            agent: Agente seleccionado
            task_type: Tipo de tarea

        Returns:
            True si el agente tiene la capacidad (o si no se puede verificar)
        """
        caps = self._load_capabilities()
        agents_caps = caps.get("agents", {})
        agent_entry = agents_caps.get(agent.value, {})

        if not agent_entry:
            # Sin info de capabilities, permitir (graceful degradation)
            return True

        # Verificar que el agente tenga capabilities definidas
        agent_capabilities = agent_entry.get("capabilities", [])
        if not agent_capabilities:
            return True

        # Mapeo de TaskType a capabilities esperadas
        task_capability_map = {
            TaskType.RESEARCH: ["requirements_gathering", "business_analysis", "user_research", "competitive_research"],
            TaskType.ANALYSIS: ["requirements_gathering", "business_analysis", "code_analysis"],
            TaskType.ARCHITECTURE: ["system_design", "architecture_decisions", "tech_stack_selection"],
            TaskType.IMPLEMENTATION: ["coding", "frontend_development", "backend_development", "ui_components"],
            TaskType.VALIDATION: ["testing", "test_automation", "qa_analysis", "usability_testing"],
            TaskType.DOCUMENTATION: ["documentation", "api_documentation", "technical_writing"],
            TaskType.SECURITY: ["security_audit", "owasp_analysis", "vulnerability_assessment"],
            TaskType.INFRASTRUCTURE: ["ci_cd", "deployment", "infrastructure", "container_management"],
            TaskType.DATABASE: ["database_design", "query_optimization", "migrations"],
            TaskType.DESIGN: ["wireframing", "prototyping", "visual_design", "design_systems", "user_research"],
            TaskType.INTEGRATION: ["integration_design", "api_integration", "webhook_management"],
            TaskType.MIGRATION: ["code_migration", "database_migration", "modernization"],
            TaskType.PERFORMANCE: ["performance_optimization", "web_vitals", "profiling"],
            TaskType.ACCESSIBILITY: ["accessibility", "wcag_compliance", "a11y_audit"],
        }

        expected_caps = task_capability_map.get(task_type, [])
        if not expected_caps:
            return True

        # Verificar si hay al menos una capability en común
        return bool(set(agent_capabilities) & set(expected_caps))

    def delegate(self, task: str, task_type: TaskType = None,
                 variant: str = "default") -> AgentRole:
        """
        Delega una tarea al agente apropiado.
        Valida contra capabilities.yaml antes de delegar.

        Args:
            task: Descripción de la tarea
            task_type: Tipo de tarea (opcional, se infiere si no se proporciona)
            variant: Variante específica

        Returns:
            AgentRole del agente delegado
        """
        # Try to load task routing for enhanced delegation
        try:
            routing_path = Path(get_project_root()) / ".nxt" / "task-routing.yaml"
            if routing_path.exists():
                with open(routing_path) as f:
                    routing = yaml.safe_load(f)
                # Use routing boundaries to validate agent selection
                boundaries = routing.get("boundaries", {})
                # Log that routing table was consulted
        except Exception:
            pass  # Graceful degradation

        if task_type is None:
            task_type = AgentDelegator.infer_task_type(task)

        agent = AgentDelegator.delegate(task_type, variant)

        # Validar capability del agente (graceful: si falla la validación, continúa)
        if not self._validate_agent_capability(agent, task_type):
            # Log warning pero no bloquear - el mapeo puede estar desactualizado
            self.state_manager.log_decision({
                "type": "capability_warning",
                "agent": agent.value,
                "task_type": task_type.value,
                "message": f"Agent {agent.value} may lack capabilities for {task_type.value}"
            })

        # Registrar decisión
        self.state_manager.log_decision({
            "type": "delegation",
            "task": task,
            "task_type": task_type.value,
            "variant": variant,
            "agent": agent.value
        })

        # Ejecutar hook
        self.hook_manager.execute("on_agent_switch", {
            "agent": agent.value,
            "task": task
        })

        # Emitir evento de activación de agente
        if self.event_bus and EventType:
            self.event_bus.emit(EventType.AGENT_ACTIVATED, {
                "agent": agent.value,
                "task": task,
                "task_type": task_type.value,
                "variant": variant
            }, source="orchestrator")

        return agent

    def plan(self, task: str, estimated_files: int = 0,
             estimated_hours: float = 0) -> Dict[str, Any]:
        """
        Planifica la ejecución de una tarea.

        Args:
            task: Descripción de la tarea
            estimated_files: Archivos estimados
            estimated_hours: Horas estimadas

        Returns:
            Plan de ejecución completo
        """
        # Sanitize input if available
        if SELF_HEALING_AVAILABLE:
            task = InputSanitizer.sanitize_task(task)

        # Clasificar
        scale = self.classify(task, estimated_files, estimated_hours)

        # Obtener configuración y grafo
        config = TaskClassifier.get_config(scale)
        graph = WorkflowGraph.get_graph(scale)
        agents = TaskClassifier.get_agents(scale)
        execution_order = WorkflowGraph.get_execution_order(scale)

        # Crear plan
        plan = {
            "id": f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "task": task,
            "scale": scale.value,
            "track": config["track"],
            "agents": [a.value for a in agents],
            "workflow_graph": graph,
            "execution_order": execution_order,
            "estimated_phases": len(execution_order),
            "created_at": datetime.now().isoformat(),
            "status": "planned"
        }

        # Add execution tracking per agent
        plan["execution_status"] = {
            agent: "pending" for agent in plan.get("execution_order", [])
        }

        # Score-aware planning (v3.8.0): enrich plan with health scores
        scores = self._load_scores()
        if scores:
            plan["scores_at_planning"] = {
                "global_score": scores.get("global_score", 0),
                "evaluated_at": scores.get("evaluated_at", "unknown")
            }
            # Add remediation agents for critical areas (score < 5)
            remediation_agents = []
            score_warnings = []
            area_agent_map = {
                "deuda_tecnica": "nxt-dev",
                "arquitectura": "nxt-architect",
                "mantenibilidad": "nxt-tech-writer",
                "cobertura_pruebas": "nxt-qa",
                "performance": "nxt-performance",
                "seguridad": "nxt-cybersec",
                "resiliencia": "nxt-devops",
                "devops": "nxt-devops",
                "ia_modelos": "nxt-aiml",
                "infraestructura": "nxt-infra",
                "equipo": "nxt-pm",
                "producto": "nxt-pm",
            }
            for area_name, area_data in scores.get("areas", {}).items():
                area_score = area_data.get("score", 10)
                if area_score is not None and area_score < 5.0:
                    agent_name = area_agent_map.get(area_name)
                    if agent_name and agent_name not in plan["agents"]:
                        remediation_agents.append(agent_name)
                        score_warnings.append(
                            f"{area_name}: {area_score}/10 → adding {agent_name}"
                        )
            if remediation_agents:
                plan["agents"].extend(remediation_agents)
                plan["score_warnings"] = score_warnings

        # Guardar en estado
        self.state_manager.add_pending_task(plan)

        # Crear contexto de ejecución
        context = ExecutionContext(
            task=task,
            scale=scale,
            current_phase=WorkflowPhase.DISCOVER,
            pending_steps=execution_order
        )
        self.state_manager.set_context(context)

        # Registrar decisión
        self.state_manager.log_decision({
            "type": "planning",
            "task": task,
            "plan_id": plan["id"],
            "scale": scale.value,
            "agents_count": len(agents)
        })

        # Emitir evento de planificación
        if self.event_bus and EventType:
            self.event_bus.emit(EventType.TASK_PLANNED, {
                "plan_id": plan["id"],
                "task": task,
                "scale": scale.value,
                "steps": len(execution_order),
                "agents": [a.value for a in agents]
            }, source="orchestrator")

        return plan

    def get_next_step(self, plan: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Obtiene el siguiente paso a ejecutar.

        Args:
            plan: Plan de ejecución (opcional, usa el contexto actual si no se proporciona)

        Returns:
            Información del siguiente paso o None si terminó
        """
        context = self.state_manager.get_context()
        if not context:
            return None

        if not context.pending_steps:
            return None

        next_node = context.pending_steps[0]
        agent = WorkflowGraph.get_agent_for_node(next_node)

        if not agent:
            return None

        # Obtener información del agente
        agent_info = self.agents.get(agent.value)

        return {
            "step": next_node,
            "agent": agent.value,
            "agent_file": agent_info.file_path if agent_info else None,
            "phase": context.current_phase.value,
            "remaining_steps": len(context.pending_steps) - 1
        }

    def complete_step(self, step: str, artifacts: Dict[str, Any] = None):
        """
        Marca un paso como completado.

        Args:
            step: Nombre del paso
            artifacts: Artefactos producidos
        """
        context = self.state_manager.get_context()
        if not context:
            return

        # Mover paso a completados
        if step in context.pending_steps:
            context.pending_steps.remove(step)
            context.completed_steps.append(step)

        # Agregar artefactos
        if artifacts:
            context.artifacts.update(artifacts)

        # Actualizar contexto
        self.state_manager.set_context(context)

        # Ejecutar hook
        self.hook_manager.execute("on_step_complete", {
            "step": step,
            "artifacts": artifacts
        })

        # Verificar si terminó
        if not context.pending_steps:
            self.hook_manager.execute("on_workflow_complete", {
                "task": context.task,
                "total_steps": len(context.completed_steps)
            })

    # =========================================================================
    # EJECUCIÓN DIRECTA (v3.4.0)
    # =========================================================================
    #
    # NOTA: A partir de v3.4.0, la ejecución de agentes se realiza directamente
    # via los slash commands que instruyen a Claude para leer los archivos
    # de agentes y ejecutar usando sus propias herramientas (Read, Write, etc.)
    #
    # Este orquestador ahora solo provee:
    # - Análisis y clasificación de tareas
    # - Planificación de workflows
    # - Información sobre agentes disponibles
    # - NO ejecuta agentes externamente (eso lo hace Claude directamente)
    # =========================================================================

    def get_all_agent_names(self) -> List[str]:
        """
        Obtiene la lista de TODOS los nombres de agentes NXT disponibles.

        Returns:
            Lista de nombres de todos los agentes NXT
        """
        return [agent.name for agent in self.agents.list_nxt()]

    def get_agent_instructions(self, agent_name: str) -> Dict[str, Any]:
        """
        Obtiene las instrucciones para ejecutar un agente directamente.

        En v3.4.0, Claude ejecuta agentes leyendo sus archivos directamente.
        Este método retorna las instrucciones para hacerlo.

        Args:
            agent_name: Nombre del agente (ej: nxt-dev)

        Returns:
            Instrucciones para ejecutar el agente
        """
        agent_info = self.agents.get(agent_name)
        if not agent_info:
            return {
                "error": f"Agente no encontrado: {agent_name}",
                "available_agents": self.get_all_agent_names()[:10]
            }

        return {
            "agent": agent_name,
            "agent_file": agent_info.file_path,
            "instructions": f"Para ejecutar este agente, usa el slash command /nxt/{agent_name.replace('nxt-', '')}",
            "direct_execution": {
                "step_1": f"Lee el archivo: agentes/{agent_name}.md",
                "step_2": "Sigue las instrucciones del agente",
                "step_3": "Usa las herramientas disponibles (Read, Write, Edit, Bash, Grep, Glob)"
            },
            "note": "v3.8.0: La ejecución es directa, Claude lee el archivo y actúa"
        }

    def list_execution_instructions(self, task: str) -> Dict[str, Any]:
        """
        Lista las instrucciones para ejecutar una tarea con todos los agentes relevantes.

        Args:
            task: Descripción de la tarea

        Returns:
            Instrucciones completas de ejecución
        """
        # Clasificar la tarea
        scale = self.classify(task)
        config = TaskClassifier.get_config(scale)
        recommended_agents = [a.value for a in config["agents"]]

        # Todos los agentes
        all_agents = self.get_all_agent_names()

        return {
            "task": task,
            "classification": {
                "scale": scale.value,
                "track": config["track"]
            },
            "recommended_agents": recommended_agents,
            "all_agents": all_agents,
            "execution_mode": "direct",
            "how_to_execute": {
                "single_agent": "Usa /nxt/[nombre] para activar un agente específico",
                "orchestrator": "Usa /nxt/orchestrator para ejecución coordinada",
                "manual": "Lee agentes/nxt-[nombre].md y sigue las instrucciones"
            },
            "note": "v3.8.0: Ejecución directa - Claude lee archivos y actúa con sus herramientas"
        }

    def analyze_project(self, deep: bool = False) -> Dict[str, Any]:
        """
        Analiza el proyecto automáticamente sin necesidad de tarea específica.

        IMPORTANTE: Este método es de SOLO LECTURA. No crea planes ni tareas
        pendientes en state.json. Solo analiza y reporta.

        Detecta:
        - Stack tecnológico
        - Estructura del proyecto
        - TODOs y FIXMEs
        - Acciones sugeridas (informativas, NO se persisten)

        Args:
            deep: Si True, ejecuta análisis profundo con agentes

        Returns:
            Diccionario con análisis completo del proyecto
        """
        import glob
        import re

        project_root = get_project_root()
        analysis = {
            "stack": [],
            "structure": {},
            "todos": [],
            "suggested_actions": [],
            "files_analyzed": 0
        }

        # 1. Detectar stack tecnológico
        config_files = {
            "package.json": "Node.js/JavaScript",
            "package-lock.json": "npm",
            "yarn.lock": "Yarn",
            "pnpm-lock.yaml": "pnpm",
            "requirements.txt": "Python",
            "pyproject.toml": "Python (modern)",
            "Pipfile": "Python (Pipenv)",
            "poetry.lock": "Python (Poetry)",
            "Cargo.toml": "Rust",
            "go.mod": "Go",
            "pom.xml": "Java (Maven)",
            "build.gradle": "Java (Gradle)",
            "composer.json": "PHP",
            "Gemfile": "Ruby",
            "*.csproj": ".NET",
            "tsconfig.json": "TypeScript",
            "next.config.js": "Next.js",
            "nuxt.config.js": "Nuxt.js",
            "vite.config.ts": "Vite",
            "tailwind.config.js": "Tailwind CSS",
            "docker-compose.yml": "Docker Compose",
            "Dockerfile": "Docker",
            ".github/workflows": "GitHub Actions",
            ".gitlab-ci.yml": "GitLab CI",
        }

        for config_file, tech in config_files.items():
            if "*" in config_file:
                matches = list(project_root.glob(config_file))
                if matches:
                    analysis["stack"].append(tech)
            else:
                if (project_root / config_file).exists():
                    analysis["stack"].append(tech)

        # Detectar frameworks en package.json
        package_json = project_root / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    pkg = json.load(f)
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                    frameworks = {
                        "react": "React",
                        "vue": "Vue.js",
                        "angular": "Angular",
                        "@angular/core": "Angular",
                        "svelte": "Svelte",
                        "express": "Express.js",
                        "fastify": "Fastify",
                        "nest": "NestJS",
                        "@nestjs/core": "NestJS",
                        "prisma": "Prisma ORM",
                        "drizzle-orm": "Drizzle ORM",
                        "jest": "Jest",
                        "vitest": "Vitest",
                        "playwright": "Playwright",
                        "cypress": "Cypress",
                    }
                    for dep, name in frameworks.items():
                        if dep in deps:
                            analysis["stack"].append(name)
            except Exception:
                pass

        # 2. Analizar estructura del proyecto
        extensions = {
            "TypeScript": ["*.ts", "*.tsx"],
            "JavaScript": ["*.js", "*.jsx"],
            "Python": ["*.py"],
            "Go": ["*.go"],
            "Rust": ["*.rs"],
            "Java": ["*.java"],
            "CSS/Styles": ["*.css", "*.scss", "*.sass", "*.less"],
            "HTML": ["*.html", "*.htm"],
            "Markdown": ["*.md"],
            "JSON": ["*.json"],
            "YAML": ["*.yml", "*.yaml"],
        }

        for category, patterns in extensions.items():
            count = 0
            for pattern in patterns:
                count += len(list(project_root.rglob(pattern)))
            if count > 0:
                analysis["structure"][category] = count
                analysis["files_analyzed"] += count

        # Contar carpetas importantes
        important_dirs = ["src", "lib", "app", "pages", "components", "api", "tests", "test", "__tests__"]
        for dir_name in important_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                file_count = sum(1 for _ in dir_path.rglob("*") if _.is_file())
                if file_count > 0:
                    analysis["structure"][f"/{dir_name}"] = file_count

        # 3. Buscar TODOs y FIXMEs
        todo_pattern = re.compile(r"(TODO|FIXME|HACK|XXX|BUG):\s*(.+)", re.IGNORECASE)
        code_extensions = [".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs", ".java"]

        for ext in code_extensions:
            for file_path in project_root.rglob(f"*{ext}"):
                # Ignorar node_modules, .git, etc.
                if any(part in str(file_path) for part in ["node_modules", ".git", "__pycache__", "venv", ".venv"]):
                    continue
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            match = todo_pattern.search(line)
                            if match:
                                rel_path = file_path.relative_to(project_root)
                                analysis["todos"].append(
                                    f"[{match.group(1)}] {rel_path}:{line_num} - {match.group(2).strip()[:60]}"
                                )
                except Exception:
                    pass

        # Limitar TODOs
        analysis["todos"] = analysis["todos"][:50]

        # 4. Generar acciones sugeridas
        if not analysis["stack"]:
            analysis["suggested_actions"].append("Inicializar proyecto con stack tecnológico")
        else:
            analysis["suggested_actions"].append(f"Proyecto detectado: {', '.join(analysis['stack'][:3])}")

        if analysis["todos"]:
            analysis["suggested_actions"].append(f"Resolver {len(analysis['todos'])} TODOs pendientes")

        if "TypeScript" not in analysis["stack"] and "JavaScript" in analysis["stack"]:
            analysis["suggested_actions"].append("Considerar migración a TypeScript")

        if "Jest" not in analysis["stack"] and "Vitest" not in analysis["stack"]:
            analysis["suggested_actions"].append("Agregar framework de testing")

        if "Docker" not in analysis["stack"]:
            analysis["suggested_actions"].append("Configurar Docker para deployment")

        # Sugerir análisis profundo
        if deep:
            analysis["suggested_actions"].append(
                "Para análisis profundo, ejecuta: /nxt/analyst o /nxt/architect"
            )

        # SAFEGUARD: analyze NUNCA debe crear pending_tasks ni modificar state.
        # Las suggested_actions son informativas y solo se devuelven en el dict.
        # Si se necesita crear un plan, usar el método plan() explícitamente.

        return analysis

    def can_parallelize(self, steps: List[str]) -> List[List[str]]:
        """
        Determina qué pasos pueden ejecutarse en paralelo.

        Analiza dependencias y agrupa pasos que no tienen
        dependencias entre sí.

        Args:
            steps: Lista de pasos a analizar

        Returns:
            Lista de grupos de pasos paralelos
        """
        # Obtener grafo de dependencias
        context = self.state_manager.get_context()
        if not context:
            return [[s] for s in steps]  # Sin contexto, secuencial

        scale = context.scale
        graph = WorkflowGraph.get_graph(scale)

        # Análisis de dependencias
        # Pasos que no dependen de otros del mismo conjunto
        groups = []
        remaining = set(steps)

        while remaining:
            # Encontrar pasos sin dependencias pendientes
            parallel_group = []
            for step in remaining:
                # Verificar que ninguna dependencia esté pendiente
                deps = graph.get(step, [])
                if not any(d in remaining for d in deps if d != step):
                    parallel_group.append(step)

            if not parallel_group:
                # Evitar bucle infinito
                parallel_group = list(remaining)

            groups.append(parallel_group)
            remaining -= set(parallel_group)

        return groups

    # =========================================================================
    # AGENTES DE PERSISTENCIA (v3.5.1)
    # =========================================================================

    def get_persistence_agents(self) -> List[str]:
        """
        Obtiene la lista de agentes de persistencia que deben ejecutarse.

        Returns:
            Lista de nombres de agentes de persistencia
        """
        return PERSISTENCE_AGENTS.copy()

    def get_persistence_agents_for_trigger(self, trigger: str) -> List[str]:
        """
        Obtiene agentes de persistencia para un trigger específico.

        Args:
            trigger: Nombre del trigger (on_session_start, on_task_complete, etc.)

        Returns:
            Lista de agentes a ejecutar para ese trigger
        """
        return PERSISTENCE_TRIGGERS.get(trigger, [])

    def get_persistence_instructions(self) -> Dict[str, Any]:
        """
        Genera instrucciones para ejecutar los agentes de persistencia.

        Returns:
            Instrucciones detalladas para cada agente de persistencia
        """
        instructions = {
            "version": "3.8.0",
            "description": "Agentes de persistencia - se ejecutan automáticamente",
            "agents": {},
            "execution_order": [
                "nxt-context",      # 1. Cargar/guardar contexto
                "nxt-multicontext", # 2. Checkpoint de estado
                "nxt-changelog",    # 3. Registrar cambios
                "nxt-ralph",        # 4. Iteración autónoma (si aplica)
            ],
            "triggers": PERSISTENCE_TRIGGERS
        }

        for agent_name in PERSISTENCE_AGENTS:
            agent_info = self.agents.get(agent_name)
            if agent_info:
                instructions["agents"][agent_name] = {
                    "file": agent_info.file_path,
                    "slash_command": f"/nxt/{agent_name.replace('nxt-', '')}",
                    "auto_execute": True,
                    "purpose": self._get_agent_purpose(agent_name)
                }

        return instructions

    def _get_agent_purpose(self, agent_name: str) -> str:
        """Obtiene el propósito de un agente de persistencia."""
        purposes = {
            "nxt-context": "Gestionar contexto entre sesiones, guardar decisiones y patrones",
            "nxt-multicontext": "Crear checkpoints, detectar pérdida de contexto, recovery automático",
            "nxt-changelog": "Documentar cambios automáticamente, generar release notes",
            "nxt-ralph": "Desarrollo autónomo iterativo, loops de hasta 50 iteraciones",
        }
        return purposes.get(agent_name, "Agente de persistencia")

    def should_run_persistence(self, trigger: str = "always") -> Dict[str, Any]:
        """
        Determina si se deben ejecutar agentes de persistencia y cuáles.

        Args:
            trigger: Evento que dispara la verificación

        Returns:
            Información sobre qué agentes ejecutar
        """
        agents_to_run = self.get_persistence_agents_for_trigger(trigger)

        # Agregar agentes "always" si no están incluidos
        always_agents = PERSISTENCE_TRIGGERS.get("always", [])
        for agent in always_agents:
            if agent not in agents_to_run:
                agents_to_run.append(agent)

        return {
            "trigger": trigger,
            "should_run": len(agents_to_run) > 0,
            "agents": agents_to_run,
            "instructions": [
                f"Lee agentes/{agent}.md y ejecuta sus instrucciones"
                for agent in agents_to_run
            ]
        }

    def format_persistence_reminder(self) -> str:
        """
        Genera un recordatorio formateado sobre los agentes de persistencia.

        Returns:
            String formateado para mostrar al usuario
        """
        lines = [
            "",
            "=" * 66,
            "  🔄 AGENTES DE PERSISTENCIA - EJECUCIÓN AUTOMÁTICA",
            "=" * 66,
            "",
            "Los siguientes agentes se ejecutan automáticamente para mantener",
            "el contexto y documentación siempre actualizados:",
            "",
        ]

        for agent in PERSISTENCE_AGENTS:
            purpose = self._get_agent_purpose(agent)
            lines.append(f"  • {agent}: {purpose}")

        lines.extend([
            "",
            "Triggers de ejecución:",
            "  - on_session_start: Al iniciar cualquier sesión",
            "  - on_task_complete: Al completar una tarea",
            "  - on_agent_switch: Al cambiar de agente",
            "  - on_checkpoint: Al crear un checkpoint manual",
            "  - on_session_end: Al terminar la sesión",
            "",
            "=" * 66,
            ""
        ])

        return "\n".join(lines)

    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del orquestador."""
        context = self.state_manager.get_context()

        status_data = {
            "version": "3.8.0",
            "framework_version": self.state_manager.state.get("framework_version", "3.8.0"),
            "current_context": {
                "task": context.task if context else None,
                "scale": context.scale.value if context else None,
                "phase": context.current_phase.value if context else None,
                "progress": f"{len(context.completed_steps)}/{len(context.completed_steps) + len(context.pending_steps)}" if context else "0/0"
            } if context else None,
            "registries": {
                "agents": {
                    "nxt": len(self.agents.list_nxt()),
                    "bmad": len(self.agents.list_bmad()),
                    "total": len(self.agents.list_all())
                },
                "skills": len(self.skills.list_all()),
                "workflows": len(self.workflows.list_all())
            },
            "execution_mode": {
                "mode": "direct",
                "description": "Claude ejecuta agentes directamente leyendo archivos .md",
                "how_to_use": "Usa /nxt/[agente] para activar un agente"
            },
            "pending_tasks": len(self.state_manager.state.get("pending_tasks", [])),
            "completed_tasks": len(self.state_manager.state.get("completed_tasks", [])),
            "active_agents": self.state_manager.state.get("active_agents", []),
            "hooks_available": list(self.hook_manager.hooks.keys()),
            "persistence_agents": {
                "agents": PERSISTENCE_AGENTS,
                "auto_execute": True,
                "triggers": list(PERSISTENCE_TRIGGERS.keys())
            },
            "last_updated": self.state_manager.state.get("last_updated"),
        }

        # Health metrics (Self-Healing Manager)
        if SELF_HEALING_AVAILABLE:
            try:
                shm = SelfHealingManager(str(self.root))
                prev_health = shm.load_previous()
                status_data["health"] = prev_health if prev_health else {"status": "NO_DATA"}
            except Exception:
                status_data["health"] = {"status": "UNAVAILABLE"}

        return status_data

    def format_plan_output(self, plan: Dict[str, Any]) -> str:
        """Formatea el plan para output legible."""
        lines = []
        lines.append("=" * 60)
        lines.append("  NXT ORCHESTRATOR v3 - Plan de Ejecución")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"📋 **Tarea:** {plan['task']}")
        lines.append(f"📊 **Escala:** {plan['scale']} ({plan['track']})")
        lines.append(f"👥 **Agentes:** {len(plan['agents'])}")
        lines.append(f"📈 **Fases:** {plan['estimated_phases']}")
        lines.append("")
        lines.append("### Agentes Involucrados")
        for agent in plan['agents']:
            lines.append(f"  • {agent}")
        lines.append("")
        lines.append("### Orden de Ejecución")
        for i, step in enumerate(plan['execution_order'], 1):
            lines.append(f"  {i}. {step}")
        lines.append("")
        lines.append("### Grafo de Workflow")
        for node, nexts in plan['workflow_graph'].items():
            if node not in ['start', 'end']:
                lines.append(f"  {node} → {', '.join(nexts)}")
        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

def main():
    """Función principal CLI."""
    # Configurar stdout para UTF-8 en Windows
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(
        description="NXT Orchestrator v3 - Sistema de 5 Niveles BMAD"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Comando: plan
    plan_parser = subparsers.add_parser("plan", help="Planificar tarea")
    plan_parser.add_argument("task", help="Descripción de la tarea")
    plan_parser.add_argument("--files", type=int, default=0, help="Archivos estimados")
    plan_parser.add_argument("--hours", type=float, default=0, help="Horas estimadas")

    # Comando: classify
    classify_parser = subparsers.add_parser("classify", help="Clasificar escala de tarea")
    classify_parser.add_argument("task", help="Descripción de la tarea")
    classify_parser.add_argument("--files", type=int, default=0)
    classify_parser.add_argument("--hours", type=float, default=0)

    # Comando: delegate
    delegate_parser = subparsers.add_parser("delegate", help="Delegar tarea a agente")
    delegate_parser.add_argument("task", help="Descripción de la tarea")
    delegate_parser.add_argument("--type", choices=[t.value for t in TaskType])
    delegate_parser.add_argument("--variant", default="default")

    # Comando: status
    subparsers.add_parser("status", help="Ver estado actual")

    # Comando: next
    subparsers.add_parser("next", help="Obtener siguiente paso")

    # Comando: complete
    complete_parser = subparsers.add_parser("complete", help="Marcar paso completado")
    complete_parser.add_argument("step", help="Nombre del paso")

    # Comando: agents
    subparsers.add_parser("agents", help="Listar agentes disponibles")

    # Comando: skills
    subparsers.add_parser("skills", help="Listar skills disponibles")

    # Comando: workflows
    subparsers.add_parser("workflows", help="Listar workflows disponibles")

    # Comando: how-to (v3.4.0 - instrucciones de ejecución)
    howto_parser = subparsers.add_parser("how-to", help="Mostrar cómo ejecutar agentes (v3.4.0)")
    howto_parser.add_argument("task", nargs="?", default="", help="Descripción de la tarea (opcional)")

    # Comando: agent-info (v3.4.0 - info de un agente)
    info_parser = subparsers.add_parser("agent-info", help="Información de un agente específico")
    info_parser.add_argument("agent", help="Nombre del agente (ej: nxt-dev)")

    # Comando: analyze (analizar proyecto automáticamente)
    analyze_parser = subparsers.add_parser("analyze", help="Analizar proyecto automáticamente")
    analyze_parser.add_argument("--deep", action="store_true", help="Sugerir análisis profundo")

    # Comando: persistence (v3.5.1 - agentes de persistencia)
    persist_parser = subparsers.add_parser("persistence", help="Mostrar agentes de persistencia (v3.5.1)")
    persist_parser.add_argument("--trigger", default="always",
                                help="Trigger específico (on_session_start, on_task_complete, etc.)")

    # Comando: health (v3.8.0 - Self-Healing)
    subparsers.add_parser("health", help="Show health metrics and circuit breaker status")

    # Comando: self-test (v3.8.0 - Self-Healing)
    subparsers.add_parser("self-test", help="Run self-healing system self-test")

    # Comando: telemetry (v3.8.0 - analytics de uso)
    telemetry_parser = subparsers.add_parser("telemetry", help="Analytics de uso del framework (v3.8.0)")
    telemetry_parser.add_argument("action", nargs="?", default="stats",
                                   choices=["stats", "flush", "status", "prune", "identify", "supabase-test"],
                                   help="stats|flush|status|prune|identify|supabase-test")
    telemetry_parser.add_argument("--days", type=int, default=30,
                                   help="Días a incluir en stats (default: 30)")
    telemetry_parser.add_argument("--user", default=None,
                                   help="Filtrar por nombre de usuario")
    telemetry_parser.add_argument("--json", action="store_true", dest="json_output",
                                   help="Output en formato JSON")

    # Comando: scores (v3.8.0 - health scores)
    subparsers.add_parser("scores", help="Ver scores de salud del proyecto (v3.8.0)")

    args = parser.parse_args()

    try:
        orchestrator = NXTOrchestratorV3()

        if args.command == "plan":
            plan = orchestrator.plan(args.task, args.files, args.hours)
            print(orchestrator.format_plan_output(plan))

        elif args.command == "classify":
            scale = orchestrator.classify(args.task, args.files, args.hours)
            config = TaskClassifier.get_config(scale)
            print(json.dumps({
                "task": args.task,
                "scale": scale.value,
                "track": config["track"],
                "max_hours": config["max_hours"],
                "agents_required": len(config["agents"])
            }, indent=2, ensure_ascii=False))

        elif args.command == "delegate":
            task_type = TaskType(args.type) if args.type else None
            agent = orchestrator.delegate(args.task, task_type, args.variant)
            agent_info = orchestrator.agents.get(agent.value)
            print(json.dumps({
                "task": args.task,
                "agent": agent.value,
                "agent_file": agent_info.file_path if agent_info else None
            }, indent=2, ensure_ascii=False))

        elif args.command == "status":
            status = orchestrator.get_status()

            # Human-readable formatted output
            print("\n" + "=" * 60)
            print("  NXT ORCHESTRATOR - Estado del Sistema")
            print("=" * 60)

            # Framework version
            fw_version = status.get("framework_version", status.get("version", "?"))
            print(f"\n  Framework Version: v{fw_version}")

            # Registries: agents, skills
            registries = status.get("registries", {})
            agents_info = registries.get("agents", {})
            nxt_count = agents_info.get("nxt", 0)
            bmad_count = agents_info.get("bmad", 0)
            total_agents = agents_info.get("total", nxt_count + bmad_count)
            skills_count = registries.get("skills", 0)
            workflows_count = registries.get("workflows", 0)
            print(f"  Agents: {total_agents} (NXT: {nxt_count}, BMAD: {bmad_count})")
            print(f"  Skills: {skills_count}")
            print(f"  Workflows: {workflows_count}")

            # Pending / completed tasks
            pending = status.get("pending_tasks", 0)
            completed = status.get("completed_tasks", 0)
            print(f"\n  Pending Tasks: {pending}")
            print(f"  Completed Tasks: {completed}")

            # Current context
            ctx = status.get("current_context")
            if ctx and ctx.get("task"):
                print(f"\n  Active Task: {ctx['task']}")
                print(f"  Phase: {ctx.get('phase', '?')}")
                print(f"  Progress: {ctx.get('progress', '?')}")

            # Telemetry status
            try:
                config = load_config()
                telemetry_cfg = config.get("telemetria", {})
                tel_enabled = telemetry_cfg.get("habilitado", False)
                supa_enabled = telemetry_cfg.get("supabase", {}).get("habilitado", False)
                tel_status = "enabled" if tel_enabled else "disabled"
                if tel_enabled and supa_enabled:
                    tel_status += " (Supabase: on)"
                elif tel_enabled:
                    tel_status += " (local only)"
            except Exception:
                tel_status = "unknown"
            print(f"\n  Telemetry: {tel_status}")

            # Last activity
            last_updated = status.get("last_updated")
            if last_updated:
                print(f"  Last Activity: {last_updated}")

            print("\n" + "=" * 60)

            # Also output JSON for programmatic use
            print("\nJSON:")
            print(json.dumps(status, indent=2, ensure_ascii=False))

        elif args.command == "next":
            next_step = orchestrator.get_next_step()
            if next_step:
                print(json.dumps(next_step, indent=2, ensure_ascii=False))
            else:
                print(json.dumps({"message": "No hay pasos pendientes"}, indent=2))

        elif args.command == "complete":
            orchestrator.complete_step(args.step)
            print(json.dumps({"message": f"Paso '{args.step}' completado"}, indent=2))

        elif args.command == "agents":
            agents = orchestrator.agents.list_all()
            print(f"\n📋 Agentes Disponibles ({len(agents)})\n")
            print("NXT Agents:")
            for a in orchestrator.agents.list_nxt():
                print(f"  • {a.name}")
            print("\nBMAD Agents:")
            for a in orchestrator.agents.list_bmad():
                print(f"  • {a.name}")

        elif args.command == "skills":
            skills = orchestrator.skills.list_all()
            print(f"\n🔧 Skills Disponibles ({len(skills)})\n")
            categories = set(s.category for s in skills)
            for cat in sorted(categories):
                print(f"{cat}:")
                for s in orchestrator.skills.get_by_category(cat):
                    print(f"  • {s.name}")

        elif args.command == "workflows":
            workflows = orchestrator.workflows.list_all()
            print(f"\n📊 Workflows Disponibles ({len(workflows)})\n")
            for phase in WorkflowPhase:
                phase_wfs = orchestrator.workflows.get_by_phase(phase)
                if phase_wfs:
                    print(f"{phase.value}:")
                    for w in phase_wfs:
                        prefix = "[BMAD]" if w.is_bmad else "[NXT]"
                        print(f"  • {prefix} {w.name}")

        elif args.command == "how-to":
            # Mostrar instrucciones de ejecución (v3.4.0)
            if args.task:
                instructions = orchestrator.list_execution_instructions(args.task)
            else:
                instructions = {
                    "execution_mode": "direct",
                    "version": "3.8.0",
                    "how_to_execute": {
                        "single_agent": "Usa /nxt/[nombre] para activar un agente",
                        "orchestrator": "Usa /nxt/orchestrator para coordinación automática",
                        "manual": "Lee agentes/nxt-[nombre].md y sigue las instrucciones"
                    },
                    "available_agents": orchestrator.get_all_agent_names()[:15],
                    "note": "En v3.8.0, Claude ejecuta agentes directamente leyendo sus archivos"
                }

            print("\n" + "="*60)
            print("  🚀 NXT ORCHESTRATOR v3.8.0 - Ejecución Directa")
            print("="*60)
            print("\n📋 CÓMO EJECUTAR AGENTES:\n")
            print("  1. Usa un slash command:")
            print("     /nxt/dev          - Activar desarrollador")
            print("     /nxt/qa           - Activar QA")
            print("     /nxt/orchestrator - Coordinación automática")
            print("")
            print("  2. Los slash commands instruyen a Claude para:")
            print("     - Leer el archivo del agente (agentes/nxt-*.md)")
            print("     - Seguir las instrucciones del agente")
            print("     - Usar herramientas: Read, Write, Edit, Bash, Grep, Glob")
            print("")
            print("  3. No se requiere API key ni proceso externo")
            print("="*60 + "\n")

            print(json.dumps(instructions, indent=2, ensure_ascii=False))

        elif args.command == "agent-info":
            # Información de un agente específico
            instructions = orchestrator.get_agent_instructions(args.agent)
            print("\n" + "="*60)
            print(f"  📋 Agente: {args.agent}")
            print("="*60 + "\n")
            print(json.dumps(instructions, indent=2, ensure_ascii=False))

        elif args.command == "analyze":
            # Analizar proyecto automáticamente
            analysis = orchestrator.analyze_project(deep=args.deep)

            print("\n" + "="*66)
            print("  🎯 NXT ORCHESTRATOR v3.8.0 - Análisis Completado")
            print("="*66)

            print("\n📊 STACK DETECTADO")
            print("━"*40)
            for tech in analysis.get("stack", []):
                print(f"  ✓ {tech}")

            print("\n📁 ESTRUCTURA")
            print("━"*40)
            structure = analysis.get("structure", {})
            for folder, count in structure.items():
                print(f"  {folder}: {count} archivos")

            print("\n📋 TAREAS PENDIENTES")
            print("━"*40)
            todos = analysis.get("todos", [])
            if todos:
                for todo in todos[:10]:  # Máximo 10
                    print(f"  → {todo}")
                if len(todos) > 10:
                    print(f"  ... y {len(todos) - 10} más")
            else:
                print("  (ninguna encontrada)")

            print("\n🎯 PLAN DE ACCIÓN SUGERIDO")
            print("━"*40)
            for i, action in enumerate(analysis.get("suggested_actions", [])[:5], 1):
                print(f"  {i}. {action}")

            print("\n" + "="*66)

            # Devolver JSON para integración
            print("\n📤 JSON para integración:")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))

        elif args.command == "persistence":
            # Mostrar agentes de persistencia (v3.5.1)
            print(orchestrator.format_persistence_reminder())

            # Mostrar qué agentes ejecutar para el trigger
            persistence_info = orchestrator.should_run_persistence(args.trigger)
            print(f"\n📋 Agentes para trigger '{args.trigger}':")
            for agent in persistence_info["agents"]:
                print(f"  → {agent}")

            print("\n🔄 Instrucciones de ejecución:")
            for instruction in persistence_info["instructions"]:
                print(f"  {instruction}")

            print("\n📤 JSON para integración:")
            print(json.dumps(orchestrator.get_persistence_instructions(), indent=2, ensure_ascii=False))

        elif args.command == "telemetry":
            # Analytics de uso (v3.8.0)
            from nxt_telemetry import (
                get_local_stats, format_stats_table, flush_to_webhook,
                get_telemetry_status, prune_events, identify_user
            )

            if args.action == "stats":
                stats = get_local_stats(days=args.days, user_filter=args.user)
                if args.json_output:
                    print(json.dumps(stats, indent=2, ensure_ascii=False))
                else:
                    print(format_stats_table(stats))

            elif args.action == "flush":
                result = flush_to_webhook()
                print(json.dumps(result, indent=2, ensure_ascii=False))

            elif args.action == "status":
                status = get_telemetry_status()
                if args.json_output:
                    print(json.dumps(status, indent=2, ensure_ascii=False))
                else:
                    s = status
                    print("\n" + "=" * 60)
                    print("  NXT TELEMETRY - Estado (v3.8.0)")
                    print("=" * 60)
                    print(f"  Habilitado: {s['habilitado']}")
                    u = s['usuario_actual']
                    print(f"  Usuario: {u['name']} ({u['email']})")
                    print(f"  Machine: {u['machine']}")
                    lo = s['local']
                    print(f"\n  LOCAL:")
                    print(f"    Archivo: {lo['archivo']}")
                    print(f"    Eventos: {lo['total_events']}")
                    print(f"    Tamaño: {lo['file_size_mb']} MB / {lo['max_size_mb']} MB")
                    print(f"    Retención: {lo['retention_days']} días")
                    w = s['webhook']
                    print(f"\n  WEBHOOK:")
                    print(f"    Habilitado: {w['habilitado']}")
                    print(f"    URL: {w['url'] or '(no configurado)'}")
                    print(f"    Pendientes sync: {lo['pending_sync']}")
                    print("=" * 60)

            elif args.action == "prune":
                result = prune_events()
                print(f"Pruned: {result['pruned']} eliminados, {result['kept']} conservados")

            elif args.action == "identify":
                user = identify_user()
                print(json.dumps(user, indent=2, ensure_ascii=False))

            elif args.action == "supabase-test":
                from nxt_telemetry import supabase_test_connection, TelemetryConfig
                config = TelemetryConfig.load()
                print(f"\nSupabase URL: {config.supabase_url}")
                print(f"Habilitado: {config.supabase_habilitado}")
                result = supabase_test_connection(config)
                print(f"Conexión: {json.dumps(result, indent=2, ensure_ascii=False)}")

        elif args.command == "health":
            if SELF_HEALING_AVAILABLE:
                shm = SelfHealingManager(str(orchestrator.root))
                prev = shm.load_previous()
                print(json.dumps(prev if prev else {"status": "NO_DATA"}, indent=2))
            else:
                print(json.dumps({"error": "self_healing module not available"}, indent=2))

        elif args.command == "self-test":
            if SELF_HEALING_AVAILABLE:
                subprocess.run([sys.executable, str(Path(__file__).parent / "self_healing.py"), "test"])
            else:
                print("self_healing module not available")

        elif args.command == "scores":
            scores = orchestrator._load_scores()
            if not scores:
                print("\n" + "=" * 60)
                print("  NXT SCORER - No hay evaluacion disponible")
                print("=" * 60)
                print("  Ejecuta /nxt/scorer para generar el score card")
                print("  o: python herramientas/nxt_orchestrator_v3.py scores")
                print("=" * 60)
            else:
                print("\n" + "=" * 60)
                print("  NXT SCORER - Score Card del Proyecto")
                print("=" * 60)
                gs = scores.get("global_score", 0)
                bar_len = int(gs * 2)
                bar = "█" * bar_len + "░" * (20 - bar_len)
                print(f"\n  SCORE GLOBAL: {gs}/10  {bar}  {int(gs * 10)}%")
                print(f"  Evaluado: {scores.get('evaluated_at', 'N/A')}")
                print(f"  Tipo: {scores.get('project_type', 'N/A')}")
                print()
                print(f"  {'Area':<22} {'Score':>6}  {'Barra'}")
                print(f"  {'─' * 22} {'─' * 6}  {'─' * 22}")
                for area_name, area_data in scores.get("areas", {}).items():
                    s = area_data.get("score")
                    if s is None:
                        print(f"  {area_name:<22} {'N/A':>6}  (no aplica)")
                        continue
                    ab = int(s * 2)
                    abar = "█" * ab + "░" * (20 - ab)
                    label = "!!" if s < 5 else ""
                    print(f"  {area_name:<22} {s:>5.1f}  {abar}  {int(s * 10)}% {label}")
                print()
                for w in scores.get("top_fortalezas", []):
                    print(f"  ✓ {w['area']} ({w['score']}) - {w['reason']}")
                print()
                for c in scores.get("top_criticos", []):
                    print(f"  ✗ {c['area']} ({c['score']}) - {c['reason']}")
                print()
                for r in scores.get("agent_recommendations", []):
                    print(f"  → {r['area']}: {r['agent']} - {r['action']}")
                print("=" * 60)

        else:
            parser.print_help()

    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
