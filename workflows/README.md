# NXT Workflows v3.8.0

Workflows del framework NXT AI Development. Cada fase tiene un workflow dedicado con agentes, entregables y criterios de salida definidos.

## Fases del Desarrollo

| # | Fase | Workflow | Agente Lead | Entregable Principal |
|---|------|----------|-------------|---------------------|
| 1 | Descubrir | `1-descubrir/workflow-discovery.md` | `nxt-analyst` | `docs/1-analysis/project-brief.md` |
| 2 | Definir | `2-definir/workflow-prd.md` | `nxt-pm` | `docs/2-planning/prd.md` |
| 3 | Disenar | `3-disenar/workflow-architecture.md` | `nxt-architect` | `docs/3-solutioning/architecture.md` |
| 4 | Planificar | `4-planificar/workflow-stories.md` | `nxt-pm` | `docs/2-planning/stories/`, `docs/4-implementation/contexts/` |
| 5 | Construir | `5-construir/workflow-development.md` | `nxt-dev` | Codigo funcional con tests |
| 6 | Verificar | `6-verificar/workflow-qa.md` | `nxt-qa` | `docs/4-implementation/qa/qa-report.md` |

## Flujo Completo

```
Descubrir -> Definir -> Disenar -> Planificar -> Construir -> Verificar
```

```
[1. DESCUBRIR]  ->  [2. DEFINIR]  ->  [3. DISENAR]  ->  [4. PLANIFICAR]  ->  [5. CONSTRUIR]  ->  [6. VERIFICAR]
  nxt-analyst        nxt-pm           nxt-architect       nxt-pm              nxt-dev             nxt-qa
  Project Brief      PRD              Architecture        Stories+Contexts    Codigo+Tests        QA Report
                                                                                  |                   |
                                                                                  +<-- FAIL (bugs) ---+
                                                                                                      |
                                                                                                 PASS -> DONE
```

## Mapa de Dependencias Entre Fases

| Fase Origen | Entregable | Fase Destino |
|-------------|-----------|--------------|
| Descubrir | `docs/1-analysis/project-brief.md` | Definir |
| Descubrir | `docs/1-analysis/user-personas.md` | Definir |
| Definir | `docs/2-planning/prd.md` | Disenar |
| Definir | `docs/2-planning/stories/` | Planificar |
| Disenar | `docs/3-solutioning/architecture.md` | Planificar, Construir |
| Disenar | `docs/3-solutioning/tech-specs/` | Construir |
| Disenar | `docs/3-solutioning/ux/` | Construir |
| Planificar | `docs/2-planning/stories/` (con criterios) | Construir |
| Planificar | `docs/4-implementation/contexts/` | Construir |
| Construir | Codigo + Tests + PR | Verificar |
| Verificar | QA Report (PASS) | Done / Deploy |
| Verificar | Bug Reports (FAIL) | Construir (re-work) |

## Workflows Especiales

| Workflow | Archivo | Descripción |
|----------|---------|-------------|
| Quick Dev | `quick-dev.md` | Bypass analysis para tareas nivel 0-1 (< 1 hora) |
| Mobile Dev | `workflow-mobile-dev.md` | Desarrollo de apps móviles - 7 fases (Spec → Monitor) |
| Shard Doc | `shard-doc.md` | Dividir documentos grandes en partes |
| Vendoring | `vendoring.md` | Bundles standalone de workflows |

## Comandos por Fase

| Fase | Comando Slash | CLI |
|------|--------------|-----|
| Descubrir | `/nxt/analyst` | `python herramientas/nxt_orchestrator_v3.py run-agent nxt-analyst "tarea"` |
| Definir | `/nxt/pm` | `python herramientas/nxt_orchestrator_v3.py run-agent nxt-pm "tarea"` |
| Disenar | `/nxt/architect` | `python herramientas/nxt_orchestrator_v3.py run-agent nxt-architect "tarea"` |
| Planificar | `/nxt/pm` | `python herramientas/nxt_orchestrator_v3.py run-agent nxt-pm "tarea"` |
| Construir | `/nxt/dev` | `python herramientas/nxt_orchestrator_v3.py run-agent nxt-dev "tarea"` |
| Verificar | `/nxt/qa` | `python herramientas/nxt_orchestrator_v3.py run-agent nxt-qa "tarea"` |
