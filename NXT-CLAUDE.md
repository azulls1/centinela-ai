# NXT AI Development Framework v3.8.0

> **"Construyendo el futuro, un sprint a la vez"**

Este proyecto utiliza el marco de desarrollo **NXT AI Development** de Grupo NXT.

---

## MODELO DE EJECUCIÓN v3.8.0 - EJECUCIÓN DIRECTA + PERSISTENCIA + TELEMETRÍA

> **Cambio fundamental en v3.4.0+**: Los slash commands ahora instruyen a Claude
> para leer archivos de agentes y ejecutar directamente usando sus herramientas.
> **No se requiere Claude CLI externo ni API keys adicionales.**
>
> **Nuevo en v3.5.1**: Agentes de persistencia AUTOMÁTICOS que se ejecutan en cada interacción.

### Cómo Funciona

| Comando | Qué Hace | Cómo Usarlo |
|---------|----------|-------------|
| `/nxt/orchestrator` | Coordina análisis del proyecto | Escribe el comando |
| `/nxt/dev` | Activa agente desarrollador | Claude lee `agentes/nxt-dev.md` |
| `/nxt/qa` | Activa agente QA | Claude lee `agentes/nxt-qa.md` |
| **Python CLI** | Información y planificación | `python herramientas/nxt_orchestrator_v3.py status` |

### Slash Commands = Ejecución Directa

Los slash commands instruyen a Claude para:
1. **Leer** el archivo del agente (`agentes/nxt-*.md`)
2. **Seguir** las instrucciones del agente
3. **Usar** herramientas disponibles: Read, Write, Edit, Bash, Grep, Glob

### CLI Python (Información y Planificación)

```bash
# Ver estado del sistema
python herramientas/nxt_orchestrator_v3.py status

# Analizar proyecto automáticamente
python herramientas/nxt_orchestrator_v3.py analyze

# Clasificar una tarea
python herramientas/nxt_orchestrator_v3.py classify "implementar auth"

# Planificar ejecución
python herramientas/nxt_orchestrator_v3.py plan "nueva feature"

# Ver cómo ejecutar agentes
python herramientas/nxt_orchestrator_v3.py how-to

# Listar agentes disponibles
python herramientas/nxt_orchestrator_v3.py agents
```

---

## REGLAS CRÍTICAS - LEER PRIMERO

### REGLA #1: AUTONOMÍA TOTAL - NUNCA PREGUNTAR

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AL RECIBIR CUALQUIER TAREA O COMANDO /nxt/:                                │
│                                                                             │
│  1. EJECUTAR: python herramientas/nxt_orchestrator_v3.py analyze           │
│  2. LEER archivos del proyecto (package.json, README.md, etc.)             │
│  3. BUSCAR TODOs con Grep                                                   │
│  4. MOSTRAR resumen y plan de acción                                        │
│  5. EJECUTAR plan sin preguntar                                             │
│                                                                             │
│  ❌ PROHIBIDO: "¿Quieres que...?", "¿Procedo?", "¿Tarea a ejecutar?"       │
│  ✅ CORRECTO: "Analizando...", "Ejecutando...", "Delegando a..."           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### REGLA #2: AL ACTIVAR /nxt/orchestrator - EJECUTAR INMEDIATAMENTE

**PASO 1** - Ejecutar con Bash:
```bash
python herramientas/nxt_orchestrator_v3.py analyze
```

**PASO 2** - Leer archivos clave del proyecto (en paralelo con Read):
- package.json, requirements.txt, README.md, CLAUDE.md

**PASO 3** - Buscar tareas pendientes (con Grep):
```
TODO:|FIXME:|HACK:|XXX:
```

**PASO 4** - Mostrar resumen con plan de acción

**PASO 5** - Si hay tarea específica, leer el agente apropiado y ejecutar

### REGLA #3: LEER AGENTES ANTES DE ACTUAR

Cada agente tiene instrucciones específicas en `agentes/nxt-*.md`.
**SIEMPRE** leer el archivo del agente antes de ejecutar su especialidad.

### REGLA #4: AGENTES DE PERSISTENCIA - EJECUCIÓN EN CADA INTERACCIÓN (v3.5.1)

```
╔═════════════════════════════════════════════════════════════════════════════╗
║  🔄 AGENTES DE PERSISTENCIA - CORAZÓN DEL FRAMEWORK                         ║
╠═════════════════════════════════════════════════════════════════════════════╣
║                                                                             ║
║  ⚠️  REGLA CRÍTICA: EJECUTAR EN CADA MENSAJE DEL USUARIO                    ║
║                                                                             ║
║  CADA VEZ que el usuario envía un mensaje o hace una petición,              ║
║  Claude DEBE ejecutar TODOS estos agentes:                                  ║
║                                                                             ║
║  ┌─────────────────┬────────────────────────────────────────────────────┐  ║
║  │ nxt-context     │ Cargar/guardar contexto de la sesión               │  ║
║  │ nxt-multicontext│ Mantener checkpoints y estado persistente          │  ║
║  │ nxt-changelog   │ Documentar cambios realizados (con anti-loop)      │  ║
║  │ nxt-ralph       │ Evaluar si hay tareas iterativas pendientes        │  ║
║  └─────────────────┴────────────────────────────────────────────────────┘  ║
║                                                                             ║
║  FLUJO DE CADA INTERACCIÓN:                                                 ║
║  ┌─────────────────────────────────────────────────────────────────────┐   ║
║  │  1. Usuario envía mensaje                                           │   ║
║  │  2. Claude lee .nxt/state.json (contexto previo)                    │   ║
║  │  3. Claude ejecuta la tarea solicitada                              │   ║
║  │  4. Claude actualiza contexto (nxt-context)                         │   ║
║  │  5. Claude crea checkpoint si hay cambios (nxt-multicontext)        │   ║
║  │  6. Claude documenta cambios significativos (nxt-changelog)         │   ║
║  │  7. Claude evalúa tareas pendientes (nxt-ralph)                     │   ║
║  └─────────────────────────────────────────────────────────────────────┘   ║
║                                                                             ║
║  TRIGGER "always" = TODOS los agentes en CADA interacción                   ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝
```

**¿POR QUÉ ES CRÍTICO?**
Estos agentes son el **sistema de memoria** del framework:
- Sin `nxt-context`: Claude olvida decisiones y preferencias entre mensajes
- Sin `nxt-multicontext`: No hay recovery si el contexto se compacta
- Sin `nxt-changelog`: No hay documentación automática de cambios
- Sin `nxt-ralph`: Las tareas complejas no se iteran correctamente

**EJECUCIÓN OBLIGATORIA EN CADA MENSAJE:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AL RECIBIR CUALQUIER MENSAJE DEL USUARIO:                                  │
│                                                                             │
│  PASO 0 (ANTES de cualquier otra cosa):                                     │
│  → Leer .nxt/state.json                                                     │
│  → Verificar contexto de agentes/nxt-context.md                             │
│  → Verificar checkpoints de agentes/nxt-multicontext.md                     │
│                                                                             │
│  PASO FINAL (DESPUÉS de completar la tarea):                                │
│  → Actualizar .nxt/state.json con nuevo contexto                            │
│  → Documentar cambios si son significativos (nxt-changelog)                 │
│  → Crear checkpoint si hubo cambios importantes (nxt-multicontext)          │
└─────────────────────────────────────────────────────────────────────────────┘
```

**COMANDOS MANUALES (si se necesita forzar):**
```
/nxt/context      → Gestionar contexto manualmente
/nxt/checkpoint   → Crear checkpoint manual
/nxt/resume       → Recuperar desde checkpoint
/nxt/changelog    → Generar changelog de cambios
```

**CLI:**
```bash
python herramientas/nxt_orchestrator_v3.py persistence
python herramientas/nxt_orchestrator_v3.py persistence --trigger always
```

---

## Historial de Versiones

> **Changelog completo**: Ver `CHANGELOG.md`
>
> **Versión actual**: 3.8.0 (2026-03-20)
> **Cambios destacados v3.8.0**: Track System (web/mobile), Self-Healing Manager,
> 34 agentes, 28 skills, 44 comandos, telemetría Supabase, equipo móvil completo.

---

## REGLA OBLIGATORIA - Comportamiento AUTÓNOMO

**IMPORTANTE: El framework NXT opera de forma AUTÓNOMA. NO PREGUNTES, ACTÚA.**

> **Reglas detalladas:** Ver `.claude/rules/agent-usage.md` para la guia completa de delegacion.

### Principio Fundamental: AUTONOMÍA TOTAL

```
╔═══════════════════════════════════════════════════════════════════════════╗
║  PROHIBIDO TERMINANTEMENTE:                                                ║
║  ❌ "¿Quieres que ejecute...?"    ❌ "¿Continúo con...?"                  ║
║  ❌ "¿Deseas que analice...?"     ❌ "¿Procedo con...?"                   ║
║  ❌ "¿Te gustaría que...?"        ❌ "¿Debería...?"                       ║
║                                                                            ║
║  OBLIGATORIO:                                                              ║
║  ✅ "Ejecutando..."  ✅ "Analizando..."  ✅ "Delegando a..."              ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

**REGLA DE RELEVANCIA:** Activar los agentes RELEVANTES para la tarea.
El orchestrator determina qué agentes participan según el nivel BMAD:
- Nivel 0-1: 1-2 agentes (dev, qa)
- Nivel 2: 4-5 agentes (según tipo de tarea)
- Nivel 3: Team completo (8-10 agentes relevantes)
- Nivel 4: Todos los agentes necesarios (multi-sprint)
No cargar agentes innecesarios - cada agente consume tokens del contexto.

**Comandos para ejecutar agentes:**
```bash
# Ejecutar agentes relevantes según nivel BMAD
python herramientas/nxt_orchestrator_v3.py auto "tu tarea"
```

### Comportamiento Autónomo Requerido

1. **SIEMPRE actuar sin esperar confirmación** para:
   - Leer y analizar archivos del proyecto
   - Detectar stack tecnológico y arquitectura
   - Clasificar tareas (nivel 0-4)
   - Crear planes de ejecución
   - Llamar a agentes especializados
   - Ejecutar tareas de nivel 0-2 automáticamente

2. **SOLO preguntar** cuando hay:
   - Ambigüedad REAL que no se puede resolver con contexto
   - Decisiones destructivas (eliminar archivos, resetear DB)
   - Nivel 4 (Enterprise) - validación de hitos críticos

3. **Al activar el Orquestador**, INMEDIATAMENTE:
   - Detectar tipo de proyecto (package.json, requirements.txt, etc.)
   - Analizar estructura del codebase
   - Identificar TODOs, issues, deuda técnica
   - Proponer y EJECUTAR plan de acción

4. **SIEMPRE delegar al agente apropiado** segun el tipo de tarea:

   > **Reglas detalladas de delegación:** Ver `.claude/rules/agent-usage.md`

5. **SIEMPRE leer el archivo del agente** antes de ejecutar tareas
   - Los agentes estan en `agentes/nxt-*.md`
   - Seguir las instrucciones, plantillas y checklists del agente

4. **SIEMPRE usar el workflow por fases**:
   ```
   Descubrir -> Definir -> Disenar -> Planificar -> Construir -> Verificar
   ```

5. **SIEMPRE mostrar el banner NXT** al inicio de cada sesion

### Ejemplo de Flujo AUTÓNOMO Correcto

```
Usuario: "Necesito agregar autenticacion OAuth"

Claude (INMEDIATAMENTE, sin preguntar):

🎯 NXT ORCHESTRATOR - Modo Autónomo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Clasificando tarea...
→ Nivel 3 (Complejo): Feature de autenticación OAuth
→ Agentes requeridos: Architect, API, CyberSec, QA

📋 Plan de ejecución:
1. Arquitectura de auth (nxt-architect)
2. Implementación backend (nxt-api)
3. Validación seguridad (nxt-cybersec)
4. Tests (nxt-qa)

🚀 Ejecutando Fase 1: Arquitectura
[Lee agentes/nxt-architect.md]
[Analiza codebase existente]
[Diseña flujo OAuth]

✓ Arquitectura propuesta:
  - OAuth 2.0 + PKCE
  - Providers: Google, GitHub
  - JWT tokens con refresh

🚀 Ejecutando Fase 2: Implementación...
[Lee agentes/nxt-api.md]
[Crea endpoints /auth/*]
[Implementa middleware]

✓ Implementado:
  - src/api/auth/oauth.ts
  - src/middleware/auth.ts
  - src/config/oauth-providers.ts

🚀 Ejecutando Fase 3: Seguridad...
[Validación OWASP automática]
...
```

### Anti-Patrones (NO HACER NUNCA)

❌ "¿Qué te gustaría hacer hoy?"
❌ "¿En qué puedo ayudarte?"
❌ "¿Quieres que analice el proyecto?"
❌ "¿Debería crear un plan primero?"
❌ Esperar confirmación para leer archivos
❌ Preguntar qué agente usar
❌ Pedir permiso para ejecutar tareas triviales

### Patrones Correctos (HACER SIEMPRE)

✅ "Analizando proyecto automáticamente..."
✅ "Detecté [stack], ejecutando [análisis]..."
✅ "Clasificado como nivel [X], delegando a [agente]..."
✅ "Plan creado. Ejecutando fase 1..."
✅ Actuar primero, reportar después
✅ Tomar decisiones basadas en contexto

---

## Inicio Rapido

```
/nxt/init          -> Inicializar proyecto
/nxt/orchestrator  -> Activar orquestador principal
/nxt/help          -> Ver todos los comandos
```

## Comandos Disponibles

### Generales
| Comando | Descripcion |
|---------|-------------|
| `/nxt/init` | Inicializar proyecto NXT |
| `/nxt/orchestrator` | Activar orquestador (director del equipo) |
| `/nxt/status` | Ver estado del proyecto |
| `/nxt/help` | Ayuda completa |

### Por Agente (34 agentes)
| Comando | Rol | Fase |
|---------|-----|------|
| `/nxt/analyst` | Analista de negocio | Descubrir |
| `/nxt/pm` | Product Manager | Definir/Planificar |
| `/nxt/architect` | Arquitecto de software | Disenar |
| `/nxt/design` | Product Designer (UX+UI) | Disenar/Construir |
| `/nxt/dev` | Desarrollador | Construir |
| `/nxt/qa` | QA Engineer | Verificar |
| `/nxt/docs` | Tech Writer | Documentar |
| `/nxt/scrum` | Scrum Master | Gestionar |
| `/nxt/devops` | DevOps Engineer | Deploy |
| `/nxt/cybersec` | Seguridad OWASP | Verificar |
| `/nxt/api` | Backend Developer | Construir |
| `/nxt/database` | Database Admin | Construir |
| `/nxt/integrations` | Integraciones | Construir |
| `/nxt/flows` | Data Flows | Construir |
| `/nxt/search` | Busquedas web (Gemini) | Cualquiera |
| `/nxt/media` | Multimedia (Gemini) | Cualquiera |
| `/nxt/migrator` | Migracion y modernizacion | Construir |
| `/nxt/performance` | Optimizacion y Web Vitals | Verificar |
| `/nxt/accessibility` | Accesibilidad WCAG 2.1 | Verificar |
| `/nxt/infra` | Terraform/Kubernetes | Deploy |
| `/nxt/mobile` | React Native/Flutter | Construir |
| `/nxt/data` | Data Engineering | Construir |
| `/nxt/aiml` | AI/ML Engineering | Construir |
| `/nxt/compliance` | GDPR/SOC 2/Licencias | Verificar |
| `/nxt/realtime` | WebSockets/SSE | Construir |
| `/nxt/localization` | i18n/L10n | Construir |
| `/nxt/paige` | Documentacion y Onboarding | Cualquiera |
| `/nxt/edge-case-hunter` | Review adversarial de boundaries | Verificar |
| `/nxt/scorer` | Evaluador de salud del proyecto (10 areas) | Verificar |
| `/nxt/context` | Gestion de contexto de sesion | Persistencia |
| `/nxt/multicontext` | Checkpoints y estado persistente | Persistencia |
| `/nxt/changelog` | Documentar cambios automaticamente | Persistencia |
| `/nxt/ralph` | Desarrollo autonomo iterativo | Persistencia |

## MCP Servers Integrados (18 total)

```json
// .claude/mcp.json
{
  "github": "Repos, PRs, issues, workflows",
  "filesystem": "Acceso avanzado al proyecto",
  "memory": "Memoria persistente entre sesiones",
  "postgres": "Conexion directa a PostgreSQL",
  "sqlite": "Base de datos SQLite local",
  "slack": "Notificaciones y comunicacion",
  "sentry": "Error tracking y monitoring",
  "notion": "Knowledge base y docs",
  "linear": "Project management",
  "docker": "Container management",
  "fetch": "HTTP requests externos",
  "redis": "Cache y pub/sub",
  "puppeteer": "Browser automation",
  "jira": "Gestion de tickets y sprints (Atlassian)",
  "figma": "Design handoff y tokens",
  "kubernetes": "Cluster y pod management",
  "cloudflare": "Edge deployment, Workers, CDN",
  "stripe": "Pagos, subscripciones, billing"
}
```

Para habilitar MCP servers, configura las API keys en `.env`

## Orquestacion Multi-Agente

### Inteligencia Adaptativa por Nivel (BMAD v6 Stable)

| Nivel | Nombre | Tiempo | Agentes | Documentacion | Track |
|-------|--------|--------|---------|---------------|-------|
| **0** | Trivial | < 15min | Solo Dev | Ninguna | Instant |
| **1** | Simple | 15min-1h | Dev + QA | Minima | Quick Flow (~5 min) |
| **2** | Estandar | 1-8h | Dev, QA, PM | Story + Tests | BMad Method (~15 min) |
| **3** | Complejo | 8-40h | Full Team | PRD + Arch | Full Planning |
| **4** | Enterprise | 40h+ | Multi-Team | Full Documentation | Enterprise (~30 min) |

### Workflow como Grafos (LangGraph)
```
[INICIO] -> [CLASIFICAR NIVEL] -> [DECISION]
                                      |
                +----------+----------+----------+----------+
                |          |          |          |          |
            [NIV 0]    [NIV 1]    [NIV 2]    [NIV 3]    [NIV 4]
            Instant    Quick     Standard   Complex   Enterprise
                |          |          |          |          |
            [DEV]     [DEV+QA]   [DESIGN]  [FULL]    [MULTI]
                |          |          |          |          |
                +----------+----------+----------+----------+
                                      |
                                  [REVIEW] -> [QA] -> [DEPLOY]
```

### CLI de Orquestación v3 (NUEVO)

```bash
# ====== EJECUCIÓN VIA CLAUDE CLI (REAL) ======

# Ejecutar agentes relevantes según nivel BMAD
python herramientas/nxt_orchestrator_v3.py auto "tu tarea"

# Ejecutar un agente individual via Claude CLI
python herramientas/nxt_orchestrator_v3.py run-agent nxt-dev "tu tarea"

# Ejecutar agentes en paralelo via Claude CLI
python herramientas/nxt_orchestrator_v3.py parallel \
  --agents 'nxt-analyst,nxt-dev,nxt-qa' \
  --task 'tu tarea'

# ====== PLANIFICACIÓN Y CLASIFICACIÓN ======

# Planificar tarea (usa 5 niveles BMAD)
python herramientas/nxt_orchestrator_v3.py plan "implementar autenticación"

# Clasificar escala (nivel_0 a nivel_4)
python herramientas/nxt_orchestrator_v3.py classify "fix typo in readme"

# Delegar a agente específico
python herramientas/nxt_orchestrator_v3.py delegate "crear API REST" --type implementation

# ====== INFORMACIÓN DEL SISTEMA ======

# Ver estado del orquestador
python herramientas/nxt_orchestrator_v3.py status

# Listar agentes (NXT + BMAD)
python herramientas/nxt_orchestrator_v3.py agents

# Listar skills disponibles
python herramientas/nxt_orchestrator_v3.py skills

# Listar workflows
python herramientas/nxt_orchestrator_v3.py workflows

# Ver scores de salud del proyecto
python herramientas/nxt_orchestrator_v3.py scores

# ====== HERRAMIENTAS AUXILIARES ======

# Ejecutar tarea autónomamente (dry-run)
python herramientas/agent_executor.py execute "add search feature" --dry-run

# Ver eventos del sistema
python herramientas/event_bus.py --demo

# Gestionar MCP servers
python herramientas/mcp_manager.py status
python herramientas/mcp_manager.py enable github
python herramientas/mcp_manager.py list --enabled
```

### CLI Legacy (compatible)
```bash
python herramientas/orchestrator.py plan "implementar autenticacion"
python herramientas/orchestrator.py status
python herramientas/orchestrator.py classify "fix typo in readme"
python herramientas/orchestrator.py delegate implementation
```

## Estructura del Proyecto

```
.nxt/                    # Configuracion del framework
├── nxt.config.yaml      # Config principal
├── state.json           # Estado persistente v2.0
├── version.txt          # 3.8.0
├── scores.json          # Score card del proyecto (12 áreas)
├── alerting.yaml        # Reglas de alertas
├── sops.yaml.example    # Ejemplo de secrets encryption
├── bmad-nxt-mapping.yaml   # v2.0: Mapeo BMAD ↔ NXT
├── skill-mcp-mapping.yaml  # v2.0: Mapeo Skills → MCP
├── capabilities.yaml       # v2.0: Capacidades por agente
└── checkpoints/            # v2.0: Checkpoints de ejecución

.claude/                 # Integracion Claude Code
├── commands/nxt/        # 21 slash commands
├── mcp.json             # MCP Servers config (nuevo)
└── settings.local.json

agentes/                 # 34 agentes NXT
├── nxt-orchestrator.md     # LangGraph + CrewAI + BMAD v6
├── nxt-analyst.md
├── nxt-pm.md
├── nxt-architect.md
├── nxt-design.md           # v3.6.0: Product Designer (fusion UX+UI)
├── nxt-dev.md
├── nxt-qa.md
├── nxt-tech-writer.md      # Documentacion
├── nxt-scrum-master.md     # Agile
├── nxt-devops.md           # CI/CD
├── nxt-cybersec.md         # Seguridad OWASP
├── nxt-api.md              # Backend/APIs
├── nxt-database.md         # Base de datos
├── nxt-integrations.md     # Integraciones
├── nxt-flows.md            # Flujos de datos
├── nxt-search.md
├── nxt-media.md
├── nxt-migrator.md         # v1.3.0: Migracion/Modernizacion
├── nxt-performance.md      # v1.3.0: Web Vitals/Optimizacion
├── nxt-accessibility.md    # v1.3.0: WCAG 2.1 a11y
├── nxt-infra.md            # v1.3.0: Terraform/K8s
├── nxt-mobile.md           # v1.3.0: React Native/Flutter
├── nxt-data.md             # v1.3.0: Data Engineering
├── nxt-aiml.md             # v1.3.0: AI/ML Engineering
├── nxt-compliance.md       # v1.3.0: GDPR/SOC 2
├── nxt-realtime.md         # v1.3.0: WebSockets/SSE
├── nxt-localization.md     # v1.3.0: i18n/L10n
├── nxt-paige.md            # v1.3.1: Documentación/Onboarding
├── nxt-edge-case-hunter.md # v3.8.0: Review adversarial/boundaries
├── nxt-context.md          # v3.3.0: Gestión de contexto (persistencia)
├── nxt-multicontext.md     # v3.3.0: Checkpoints multi-contexto
├── nxt-changelog.md        # v3.3.0: Changelog automático
├── nxt-ralph.md            # v3.2.0: Desarrollo autónomo iterativo
└── nxt-scorer.md           # v3.8.0: Evaluador de salud (10 areas, score card)

plugins/                 # Sistema de plugins
└── nxt-core/
    ├── manifest.json
    └── hooks/              # v2.0: Hooks del sistema
        ├── on-init.py
        ├── on-agent-switch.py
        ├── on-step-complete.py
        └── on-workflow-complete.py

herramientas/            # 19 herramientas Python + 1 SQL
├── nxt_orchestrator_v3.py  # Orquestador principal (BMAD v6, 5 niveles)
├── orchestrator.py      # Orquestador legacy (v1)
├── agent_executor.py    # Ejecución autónoma de workflows
├── event_bus.py         # Sistema de eventos pub/sub
├── mcp_manager.py       # Gestión dinámica de MCP servers
├── self_healing.py      # v3.8.0: Self-Healing, CircuitBreaker
├── nxt_telemetry.py     # v3.8.0: Telemetría Supabase
├── context_manager.py   # Persistencia de contexto
├── integration_hub.py   # Hub de integraciones
├── llm_router.py        # Router Claude/Gemini/OpenAI
├── gemini_tools.py      # Gemini API integration
├── openai_tools.py      # OpenAI API integration
├── claude_cli_client.py # Claude CLI (legacy)
├── validate_setup.py    # Validador de configuración
├── validator.py         # Validación de datos
├── stack_detector.py    # Detección automática de stack
├── vendor.py            # Workflow Vendoring
├── test_integration.py  # Tests de integración
├── utils.py             # Utilidades comunes
└── supabase_setup.sql   # Schema Supabase telemetría

docs/guides/             # v1.3.1: Documentation Guides (Diátaxis)
├── README.md            # Índice de guías
├── tutorials/           # Tutoriales paso a paso
├── how-to/              # Guías prácticas
├── explanation/         # Conceptos profundos
└── reference/           # Especificaciones técnicas

tests/                   # 17 tests automatizados
├── conftest.py
├── test_llm_router.py
├── test_orchestrator.py
├── test_orchestrator_v3.py
├── test_gemini_tools.py
├── test_openai_tools.py
├── test_integration_v3.py
├── test_security.py
├── test_telemetry.py
├── test_telemetry_e2e.py
├── test_self_healing.py
├── test_event_bus.py
├── test_context_manager.py
├── test_mcp_manager.py
├── test_stack_detector.py
├── test_eval_orchestrator.py
├── benchmark_orchestrator.py
└── load_test.py

plantillas/                # 24 plantillas (5 base + 19 entregables)
├── architecture-template.md
├── prd-template.md
├── project-brief.md
├── story-template.md
├── test-plan-template.md
└── entregables/           # 19 plantillas de entregables
    ├── project-brief.md, prd.md, user-story.md, architecture.md
    ├── tech-spec.md, epic.md, sprint-backlog.md, code-review.md
    ├── qa-report.md, security-audit.md, performance-audit.md
    ├── deployment-runbook.md, incident-response.md, threat-model.md
    ├── data-quality-report.md, ml-model-card.md, mobile-app-spec.md
    ├── wcag-remediation.md
    └── openapi-spec.yaml

skills/                  # 28 skills por categoria
├── documentos/          #   6 skills
│   ├── SKILL-docx.md
│   ├── SKILL-pdf.md
│   ├── SKILL-pptx.md
│   ├── SKILL-xlsx.md
│   ├── SKILL-api-docs.md
│   └── SKILL-markdown-advanced.md
├── desarrollo/          #   18 skills
│   ├── SKILL-testing.md
│   ├── SKILL-diagrams.md
│   ├── SKILL-migrations.md
│   ├── SKILL-monitoring.md
│   ├── SKILL-containers.md
│   ├── SKILL-security.md
│   ├── SKILL-code-quality.md
│   ├── SKILL-changelog.md
│   ├── SKILL-context-persistence.md
│   ├── SKILL-implementation-readiness.md
│   ├── SKILL-root-cause-analysis.md
│   ├── SKILL-mobile-performance.md
│   ├── SKILL-mobile-testing.md
│   ├── SKILL-mobile-ci.md
│   ├── SKILL-app-store.md
│   ├── SKILL-mobile-security.md
│   ├── SKILL-mobile-analytics.md
│   └── SKILL-mobile-ux.md
└── integraciones/       #   4 skills
    ├── SKILL-gemini.md
    ├── SKILL-openai.md
    ├── SKILL-mcp.md
    └── SKILL-webhooks.md

workflows/               # 6 fases + especiales
├── fase-1-descubrir/
├── fase-2-definir/
├── fase-3-disenar/
├── fase-4-planificar/
├── fase-5-construir/
├── fase-6-verificar/
├── shard-doc.md         # v1.3.1: Document sharding
├── brownfield.md
└── vendoring.md         # v1.3.1: Workflow bundles
scripts/                 # 4 scripts de instalación y ops
├── install-nxt.ps1      # Instalador Windows
├── install-nxt.sh       # Instalador Unix
├── onboarding.sh        # Onboarding de nuevos devs
└── backup.sh            # Backup de configuración

docs/                    # Documentacion generada
├── runbook.md           # Runbook operacional
├── safety-guidelines.md # Guías de seguridad
├── threat-model.md      # Modelo de amenazas
├── VALIDATION-GUIDE.md  # Guía de validación
└── guides/              # Diátaxis guides (ver arriba)

.claude-plugin/          # Plugin manifest para distribución
└── plugin.json

docker-compose.yml       # Container config con resource limits
pyproject.toml           # Config unificada Python (ruff, pytest, coverage)
CONTRIBUTING.md          # Guía de contribución
PLUGIN-README.md         # README del plugin

nxt/                     # BMAD Method v6
```

## Arquitectura LLM

| LLM | Uso | Modelo |
|-----|-----|--------|
| **Claude** | Codigo, documentos, razonamiento | `claude-opus-4-5-20251101` |
| **Gemini** | Busquedas, multimedia, verificacion | Ver tabla abajo |

### Modelo Claude

| Funcion | Modelo | Descripcion |
|---------|--------|-------------|
| Orquestador | `claude-opus-4-5-20251101` | Claude Opus 4.5 - El mas potente |
| Codigo | `claude-opus-4-5-20251101` | 80.9% SWE-bench |
| Documentos | `claude-opus-4-5-20251101` | 200K tokens contexto |
| Razonamiento codigo/arquitectura | `claude-opus-4-5-20251101` | Logica y decisiones tecnicas |

### Modelos Gemini

| Funcion | Modelo |
|---------|--------|
| Busquedas/Default | `gemini-3-pro-preview` |
| Razonamiento + info actual | `gemini-3-pro-preview` |
| Imagenes | `nano-banana-pro-preview` |
| Videos | `veo-3.0-generate-001` |
| TTS | `gemini-2.5-pro-preview-tts` |

## Fases de Desarrollo

1. **Descubrir** - Brainstorming, investigacion, analisis
2. **Definir** - PRD, requisitos, backlog
3. **Disenar** - Arquitectura, UX, tech spec
4. **Planificar** - Epics, stories, sprints
5. **Construir** - Codigo, tests, documentacion
6. **Verificar** - QA, validacion, regresion

## Configuracion

| Archivo | Proposito |
|---------|-----------|
| `.env` | API Keys (Gemini, OpenAI, GitHub) |
| `.nxt/nxt.config.yaml` | Config del framework |
| `.claude/mcp.json` | MCP Servers |
| `.nxt/state.json` | Estado persistente |
| `.nxt/scores.json` | Score card del proyecto (12 areas) |
| `.nxt/alerting.yaml` | Reglas de alertas |
| `pyproject.toml` | Config unificada Python (ruff, pytest, coverage) |
| `docker-compose.yml` | Container config con resource limits |

## Recursos

| Recurso | Ubicacion |
|---------|-----------|
| Agentes NXT | `agentes/nxt-*.md` |
| Skills | `skills/**/*.md` |
| Workflows | `workflows/` |
| Herramientas CLI | `herramientas/*.py` |
| Plugin manifest | `plugins/nxt-core/manifest.json` |
| MCP config | `.claude/mcp.json` |

## Soporte

- Documentacion: `nxt/README.md`
- Ejemplos: `ejemplos/`
