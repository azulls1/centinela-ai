# Workflow: Diseno de Arquitectura

## Fase
**DISENAR** (Fase 3 de 6)

## Agentes
- `nxt-architect` (Principal)
- `nxt-design` (Paralelo)

## Objetivo
Disenar la arquitectura tecnica y la experiencia de usuario del sistema.

## Triggers
- `*architecture` - Disenar arquitectura
- `*tech-spec [epic]` - Crear tech spec
- `*api-design` - Disenar APIs
- `*adr [decision]` - Crear ADR
- `*diagram [tipo]` - Generar diagrama

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────┐
│                     FASE: DISENAR                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────┐    ┌─────────────────────┐       │
│   │   NXT ARCHITECT     │    │    NXT DESIGN        │       │
│   ├─────────────────────┤    ├─────────────────────┤       │
│   │                     │    │                     │       │
│   │ 1. Revisar PRD      │    │ 1. Revisar PRD      │       │
│   │                     │    │                     │       │
│   │ 2. Disenar C4       │    │ 2. User Flows       │       │
│   │    - Context        │    │                     │       │
│   │    - Container      │    │ 3. Wireframes       │       │
│   │    - Component      │    │                     │       │
│   │                     │    │ 4. UI Components    │       │
│   │ 3. Tech Stack       │    │                     │       │
│   │                     │    │ 5. Style Guide      │       │
│   │ 4. APIs             │    │                     │       │
│   │                     │    │                     │       │
│   │ 5. Data Model       │    │                     │       │
│   │                     │    │                     │       │
│   │ 6. ADRs             │    │                     │       │
│   │                     │    │                     │       │
│   └──────────┬──────────┘    └──────────┬──────────┘       │
│              │                          │                   │
│              └──────────┬───────────────┘                   │
│                         │                                   │
│                         ▼                                   │
│              ┌─────────────────────┐                       │
│              │  TECH SPECS + UX    │                       │
│              │  INTEGRADOS         │                       │
│              └─────────────────────┘                       │
│                                                             │
│   SALIDAS:                                                  │
│   - docs/3-solutioning/architecture.md                     │
│   - docs/3-solutioning/tech-specs/                         │
│   - docs/3-solutioning/ux/                                 │
│   - docs/diagrams/                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              [Siguiente: FASE PLANIFICAR]
```

## Diagramas Requeridos

### Minimo
1. C4 Context Diagram
2. C4 Container Diagram
3. ERD (si hay base de datos)

### Recomendados
4. C4 Component Diagram (para modulos complejos)
5. Diagramas de Secuencia (para flujos criticos)
6. Deployment Diagram

## Tech Stack Selection

Al seleccionar tecnologias, documentar:

| Categoria | Opcion Elegida | Alternativas | Justificacion |
|-----------|----------------|--------------|---------------|
| Frontend | React | Vue, Angular | [Razon] |
| Backend | Node.js | Python, Go | [Razon] |
| Database | PostgreSQL | MongoDB, MySQL | [Razon] |
| Cache | Redis | Memcached | [Razon] |
| Cloud | AWS | GCP, Azure | [Razon] |

## ADR Template

```markdown
# ADR-XXX: [Titulo de la Decision]

## Estado
Propuesto | Aceptado | Deprecado | Reemplazado

## Contexto
[Por que necesitamos tomar esta decision]

## Decision
[Que decidimos hacer]

## Consecuencias
### Positivas
-

### Negativas
-

### Riesgos
-
```

## Checklist de Entregables

### Arquitectura
- [ ] Diagrama C4 Context
- [ ] Diagrama C4 Container
- [ ] Diagrama C4 Component (si aplica)
- [ ] Tech Stack documentado
- [ ] ADRs para decisiones clave
- [ ] API Design (endpoints, contratos)
- [ ] Data Model (ERD)

### UX
- [ ] User Flows principales
- [ ] Wireframes de pantallas clave
- [ ] Componentes UI definidos
- [ ] Style Guide basico

## Artefactos Generados

| Artefacto | Ubicacion | Formato |
|-----------|-----------|---------|
| Architecture Doc | `docs/3-solutioning/architecture.md` | Markdown |
| Tech Specs | `docs/3-solutioning/tech-specs/` | Markdown |
| ADRs | `docs/3-solutioning/adrs/` | Markdown |
| Diagramas | `docs/diagrams/` | SVG/PNG |
| UX Docs | `docs/3-solutioning/ux/` | Markdown |

## Criterios de Salida

Para pasar a la siguiente fase (PLANIFICAR):

1. Arquitectura de alto nivel aprobada
2. Tech stack definido y justificado
3. APIs principales disenadas
4. User flows completados
5. Al menos wireframes de pantallas principales

## Siguiente Paso

```
Al completar esta fase, ejecuta:
/nxt/pm

Esto activara el agente PM para la planificacion de sprints.
```
