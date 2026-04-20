# Workflow: Planificacion de Sprints

## Fase
**PLANIFICAR** (Fase 4 de 6)

## Agente Principal
`nxt-pm`

## Objetivo
Desglosar el trabajo en epics, stories y tareas planificables.

## Triggers
- `*create-epics` - Extraer epics del PRD
- `*create-story [epic]` - Crear story
- `*sprint-planning` - Planificar sprint
- `*story-context [story]` - Generar contexto (GAME CHANGER)

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────┐
│                    FASE: PLANIFICAR                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. EXTRAER EPICS                                          │
│      └─> Identificar epics del PRD                         │
│      └─> Priorizar epics                                   │
│      └─> Definir scope de cada epic                        │
│                                                             │
│   2. DESGLOSAR EN STORIES                                   │
│      └─> Crear stories por epic                            │
│      └─> Aplicar formato estandar                          │
│      └─> Definir criterios de aceptacion                   │
│                                                             │
│   3. ESTIMAR                                                │
│      └─> Story points (Fibonacci: 1,2,3,5,8,13)           │
│      └─> Identificar dependencias                          │
│      └─> Marcar bloqueadores                               │
│                                                             │
│   4. PLANIFICAR SPRINT                                      │
│      └─> Seleccionar stories para sprint                   │
│      └─> Verificar capacidad                               │
│      └─> Crear sprint backlog                              │
│                                                             │
│   5. GENERAR CONTEXTO (GAME CHANGER)                        │
│      └─> Analizar codebase existente                       │
│      └─> Identificar archivos a modificar                  │
│      └─> Extraer patrones de codigo                        │
│      └─> Crear contexto especifico por story               │
│                                                             │
│   SALIDAS:                                                  │
│   - docs/2-planning/epics/                                 │
│   - docs/2-planning/stories/                               │
│   - docs/4-implementation/contexts/                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              [Siguiente: FASE CONSTRUIR]
```

## Story Format

```markdown
# Story: [ID]

## Titulo
[Titulo descriptivo]

## Descripcion
**Como** [tipo de usuario]
**Quiero** [accion/funcionalidad]
**Para** [beneficio/valor]

## Criterios de Aceptacion
- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

## Notas Tecnicas
[Del arquitecto]

## Story Points
[1/2/3/5/8/13]

## Dependencias
- [Story que debe completarse antes]

## Epic
[Nombre del epic padre]

## Sprint
[Numero de sprint]

## Estado
[ ] Backlog
[ ] Ready
[ ] In Progress
[ ] In Review
[ ] Done
```

## Story Context (GAME CHANGER)

El Story Context es lo que diferencia NXT de otros frameworks.
Proporciona al desarrollador TODO lo que necesita para empezar.

### Contenido del Context

```markdown
# Story Context: [ID]

## Archivos a Modificar
| Archivo | Accion | Lineas |
|---------|--------|--------|
| src/components/X.tsx | Crear | - |
| src/api/Y.ts | Modificar | 45-67 |
| src/utils/Z.ts | Agregar funcion | - |

## Patrones del Codigo Existente

### Componentes
[Ejemplo de como se crean componentes en este proyecto]

### API Calls
[Ejemplo de como se hacen llamadas API]

### Testing
[Ejemplo de como se escriben tests]

## Codigo de Referencia
[Snippets de codigo similar existente]

## Dependencias
- [Libreria X] ya instalada
- [Servicio Y] ya implementado en src/services/

## Notas del Arquitecto
[Consideraciones especificas de arquitectura]

## Checklist de Implementacion
- [ ] Crear componente X
- [ ] Agregar endpoint Y
- [ ] Escribir tests
- [ ] Actualizar documentacion
```

## Checklist de Entregables

- [ ] Epics extraidos y priorizados
- [ ] Stories creadas con formato estandar
- [ ] Todas las stories tienen criterios de aceptacion
- [ ] Story points asignados
- [ ] Dependencias identificadas
- [ ] Sprint backlog creado
- [ ] Story contexts generados para sprint actual

## Artefactos Generados

| Artefacto | Ubicacion | Formato |
|-----------|-----------|---------|
| Epics | `docs/2-planning/epics/` | Markdown |
| Stories | `docs/2-planning/stories/` | Markdown |
| Sprint Backlog | `docs/2-planning/sprint-X/` | Markdown |
| Story Contexts | `docs/4-implementation/contexts/` | Markdown |

## Fibonacci para Story Points

| Points | Complejidad | Ejemplo |
|--------|-------------|---------|
| 1 | Trivial | Cambiar texto, ajustar estilo |
| 2 | Simple | CRUD basico, formulario simple |
| 3 | Moderado | Feature con logica, validaciones |
| 5 | Complejo | Integracion externa, flujo completo |
| 8 | Muy complejo | Modulo nuevo, arquitectura |
| 13 | Enorme | Considerar dividir |

## Criterios de Salida

Para pasar a la siguiente fase (CONSTRUIR):

1. Sprint backlog definido
2. Stories priorizadas
3. Story points asignados
4. Story contexts generados
5. Desarrollador puede empezar sin preguntas

## Siguiente Paso

```
Al completar esta fase, ejecuta:
/nxt/dev

Esto activara el agente Dev para comenzar implementacion.
El desarrollador toma la primera story y su context.
```
