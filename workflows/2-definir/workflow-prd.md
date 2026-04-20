# Workflow: Definicion de Requisitos

## Fase
**DEFINIR** (Fase 2 de 6)

## Agente Principal
`nxt-pm`

## Objetivo
Crear el PRD completo con requisitos funcionales, no funcionales y user stories.

## Triggers
- `*create-prd` - Crear PRD completo
- `*plan-project` - Planificacion adaptativa
- `*prioritize` - Priorizar features
- `*roadmap` - Crear roadmap

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────┐
│                     FASE: DEFINIR                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. REVISAR                                                │
│      └─> Leer Project Brief de fase anterior               │
│      └─> Validar entendimiento del problema                │
│      └─> Confirmar scope con stakeholders                  │
│                                                             │
│   2. DEFINIR VISION                                         │
│      └─> Articular vision del producto                     │
│      └─> Establecer objetivos medibles                     │
│      └─> Definir criterios de exito                        │
│                                                             │
│   3. REQUISITOS FUNCIONALES                                 │
│      └─> Listar features principales                       │
│      └─> Detallar cada requisito                           │
│      └─> Definir criterios de aceptacion                   │
│                                                             │
│   4. REQUISITOS NO FUNCIONALES                              │
│      └─> Performance                                       │
│      └─> Seguridad                                         │
│      └─> Escalabilidad                                     │
│      └─> Usabilidad                                        │
│                                                             │
│   5. USER STORIES                                           │
│      └─> Formato: Como [rol] quiero [accion] para [valor] │
│      └─> Criterios de aceptacion por story                 │
│      └─> Estimacion inicial (T-shirt sizing)               │
│                                                             │
│   6. PRIORIZACION                                           │
│      └─> Aplicar MoSCoW                                    │
│      └─> Identificar MVP                                   │
│      └─> Crear roadmap de releases                         │
│                                                             │
│   SALIDA: docs/2-planning/prd.md                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              [Siguiente: FASE DISENAR]
```

## Priorizacion MoSCoW

| Categoria | Significado | % Recomendado |
|-----------|-------------|---------------|
| **Must** | Imprescindible para MVP | 60% |
| **Should** | Importante pero no bloqueante | 20% |
| **Could** | Deseable si hay tiempo | 15% |
| **Won't** | Descartado para este release | 5% |

## Checklist de Entregables

- [ ] PRD completo con todas las secciones
- [ ] Requisitos funcionales detallados
- [ ] Requisitos no funcionales definidos
- [ ] User stories en formato estandar
- [ ] Criterios de aceptacion por story
- [ ] Priorizacion MoSCoW aplicada
- [ ] MVP claramente definido
- [ ] Out of scope documentado
- [ ] Riesgos identificados

## Artefactos Generados

| Artefacto | Ubicacion | Formato |
|-----------|-----------|---------|
| PRD | `docs/2-planning/prd.md` | Markdown |
| User Stories | `docs/2-planning/stories/` | Markdown |
| Backlog | `docs/2-planning/backlog.md` | Markdown |
| Roadmap | `docs/2-planning/roadmap.md` | Markdown |

## Estructura del PRD

```markdown
# PRD: [Nombre]

## 1. Vision del Producto
## 2. Objetivos de Negocio
## 3. Usuarios Objetivo
## 4. Requisitos Funcionales
## 5. Requisitos No Funcionales
## 6. User Stories
## 7. Fuera de Alcance
## 8. Dependencias
## 9. Riesgos
## 10. Timeline de Alto Nivel
## 11. Criterios de Exito
## 12. Aprobaciones
```

## Criterios de Salida

Para pasar a la siguiente fase (DISENAR):

1. PRD revisado y aprobado
2. Todas las stories tienen criterios de aceptacion
3. Priorizacion completada
4. MVP claramente definido
5. Stakeholders alineados

## Siguiente Paso

```
Al completar esta fase, ejecuta:
/nxt/architect

Esto activara el agente Architect para disenar la arquitectura.
```
