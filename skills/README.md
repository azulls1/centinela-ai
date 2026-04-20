# NXT Skills v3.8.0

> Skills son capacidades especializadas que los agentes pueden usar para completar tareas.

## Indice de Skills (19 total)

### Desarrollo (9 skills)

| Skill | Descripcion | Agentes que lo usan |
|-------|-------------|---------------------|
| [SKILL-testing](desarrollo/SKILL-testing.md) | Testing (Jest, Pytest, TDD) | nxt-qa, nxt-dev |
| [SKILL-code-quality](desarrollo/SKILL-code-quality.md) | Code review + refactoring unificado | nxt-qa, nxt-dev |
| [SKILL-diagrams](desarrollo/SKILL-diagrams.md) | Diagramas (Mermaid, PlantUML, C4) | nxt-architect, nxt-docs |
| [SKILL-migrations](desarrollo/SKILL-migrations.md) | Database migrations | nxt-database, nxt-migrator |
| [SKILL-monitoring](desarrollo/SKILL-monitoring.md) | APM, logging, alertas | nxt-devops, nxt-performance |
| [SKILL-containers](desarrollo/SKILL-containers.md) | Docker, Kubernetes | nxt-devops, nxt-infra |
| [SKILL-changelog](desarrollo/SKILL-changelog.md) | Changelog generation | nxt-changelog |
| [SKILL-context-persistence](desarrollo/SKILL-context-persistence.md) | Context persistence | nxt-context, nxt-multicontext |
| [SKILL-security](desarrollo/SKILL-security.md) | Security scanning | nxt-cybersec |

### Documentos (6 skills)

| Skill | Descripcion | Agentes que lo usan |
|-------|-------------|---------------------|
| [SKILL-docx](documentos/SKILL-docx.md) | Generacion de Word docs | nxt-docs |
| [SKILL-xlsx](documentos/SKILL-xlsx.md) | Generacion de Excel | nxt-docs, nxt-data |
| [SKILL-pptx](documentos/SKILL-pptx.md) | Generacion de PowerPoint | nxt-docs |
| [SKILL-pdf](documentos/SKILL-pdf.md) | Generacion de PDFs | nxt-docs |
| [SKILL-api-docs](documentos/SKILL-api-docs.md) | OpenAPI, Swagger, Redoc | nxt-api, nxt-docs |
| [SKILL-markdown-advanced](documentos/SKILL-markdown-advanced.md) | MDX, Mermaid, Docusaurus | nxt-docs |

### Integraciones (4 skills)

| Skill | Descripcion | Agentes que lo usan |
|-------|-------------|---------------------|
| [SKILL-gemini](integraciones/SKILL-gemini.md) | Google Gemini (busquedas, multimedia) | nxt-search, nxt-media |
| [SKILL-openai](integraciones/SKILL-openai.md) | OpenAI integration (legacy) | nxt-media |
| [SKILL-mcp](integraciones/SKILL-mcp.md) | Model Context Protocol | nxt-orchestrator |
| [SKILL-webhooks](integraciones/SKILL-webhooks.md) | Webhooks in/out | nxt-integrations, nxt-flows |

## Combinaciones Comunes de Skills

| Escenario | Skills Combinados |
|-----------|-------------------|
| Feature completa | testing + code-quality + diagrams |
| Deploy | containers + monitoring + security |
| API nueva | api-docs + testing + security |
| Migracion DB | migrations + testing + monitoring |
| Documentacion | markdown-advanced + diagrams + docx/pdf |
| Code review | code-review + code-quality + security |

## Como Activar un Skill

Los skills se activan automaticamente cuando un agente lo necesita. Tambien puedes invocarlos directamente mencionando su nombre en la conversacion.
