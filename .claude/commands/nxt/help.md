# AYUDA NXT - EJECUCION DIRECTA

**INSTRUCCION:** Muestra la ayuda del sistema NXT.

## PASO 1: Ayuda CLI
Ejecuta con Bash:
```bash
python herramientas/nxt_orchestrator_v3.py --help
```

## PASO 2: Listar agentes
Ejecuta con Bash:
```bash
python herramientas/nxt_orchestrator_v3.py agents
```

## PASO 3: Comandos disponibles
Muestra lista de todos los `/nxt/*` commands disponibles.

## Guia Rapida: ¿Que Comando Necesito?

Si no sabes que agente usar:
- Tarea simple (bug fix, typo) → `/nxt/dev tu tarea`
- Tarea compleja (feature, modulo) → `/nxt/orchestrator`
- Ver estado → `/nxt/status`
- Recuperar sesion anterior → `/nxt/resume`

Por tipo de trabajo:
- Codigo/implementacion → `/nxt/dev`
- API/endpoints → `/nxt/api`
- Base de datos → `/nxt/database`
- Testing → `/nxt/qa`
- Seguridad → `/nxt/cybersec`
- Deploy/CI-CD → `/nxt/devops`
- Documentacion → `/nxt/docs`
- Diseno UI/UX → `/nxt/design`
- Arquitectura → `/nxt/architect`

## Todos los Comandos Disponibles

### Agentes de Desarrollo (build)
| Comando | Qué Hace |
|---------|----------|
| `/nxt/dev` | Desarrollo general de código |
| `/nxt/api` | Crear/modificar endpoints REST/GraphQL |
| `/nxt/database` | Schema, migraciones, queries |
| `/nxt/design` | UX Research + UI Design + Frontend |
| `/nxt/mobile` | React Native / Flutter |
| `/nxt/realtime` | WebSockets / SSE |
| `/nxt/integrations` | APIs externas, adaptadores |
| `/nxt/flows` | Jobs, pipelines, ETL app-level |
| `/nxt/data` | Data Engineering (Airflow, dbt) |
| `/nxt/aiml` | AI/ML, RAG, fine-tuning |
| `/nxt/localization` | i18n, traducciones, RTL |

### Agentes de Calidad (verify)
| Comando | Qué Hace |
|---------|----------|
| `/nxt/qa` | Testing funcional, regresión |
| `/nxt/edge-case-hunter` | Review adversarial de boundary conditions |
| `/nxt/cybersec` | Auditoría OWASP, seguridad |
| `/nxt/performance` | Core Web Vitals, optimización |
| `/nxt/accessibility` | WCAG 2.1, a11y |
| `/nxt/compliance` | GDPR, SOC 2, licencias |

### Agentes de Planificación (plan)
| Comando | Qué Hace |
|---------|----------|
| `/nxt/analyst` | Análisis de negocio, research |
| `/nxt/pm` | PRD, user stories, backlog |
| `/nxt/architect` | Arquitectura, tech spec, ADRs |
| `/nxt/scrum` | Sprint planning, retrospectivas |

### Agentes de Infraestructura (deploy)
| Comando | Qué Hace |
|---------|----------|
| `/nxt/devops` | CI/CD, Docker, GitHub Actions |
| `/nxt/infra` | Terraform, Kubernetes, Helm |

### Agentes de Soporte
| Comando | Qué Hace |
|---------|----------|
| `/nxt/docs` | Documentación técnica |
| `/nxt/search` | Búsquedas web (Gemini) |
| `/nxt/media` | Imágenes, video, audio (Gemini) |
| `/nxt/paige` | Onboarding y guía del framework |
| `/nxt/migrator` | Migración de código, upgrades |

### Comandos de Sistema
| Comando | Qué Hace |
|---------|----------|
| `/nxt/orchestrator` | Coordinación automática de agentes |
| `/nxt/init` | Inicializar proyecto |
| `/nxt/status` | Ver estado actual |
| `/nxt/checkpoint` | Guardar estado |
| `/nxt/resume` | Recuperar sesión anterior |
| `/nxt/changelog` | Generar changelog |

**NO PREGUNTES. EJECUTA.**
