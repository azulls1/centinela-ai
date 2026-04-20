# Workflow: Descubrimiento

## Fase
**DESCUBRIR** (Fase 1 de 6)

## Agente Principal
`nxt-analyst`

## Objetivo
Investigar, analizar y documentar la vision inicial del proyecto.

## Triggers
- `/nxt/init` - Inicializar nuevo proyecto
- `*brainstorm [idea]` - Sesion de brainstorming
- `*research [tema]` - Investigacion profunda
- `*product-brief` - Crear project brief

## Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────┐
│                    FASE: DESCUBRIR                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. DETECTAR                                               │
│      └─> Escanear directorio                               │
│      └─> Identificar greenfield/brownfield                  │
│      └─> Evaluar complejidad                               │
│                                                             │
│   2. BRAINSTORM                                             │
│      └─> Generar ideas                                     │
│      └─> Explorar alternativas                             │
│      └─> Identificar innovaciones                          │
│                                                             │
│   3. INVESTIGAR                                             │
│      └─> Analizar mercado (via nxt-search)                 │
│      └─> Estudiar competencia                              │
│      └─> Validar viabilidad                                │
│                                                             │
│   4. ANALIZAR                                               │
│      └─> Crear user personas                               │
│      └─> Mapear user journeys                              │
│      └─> Identificar pain points                           │
│                                                             │
│   5. DOCUMENTAR                                             │
│      └─> Crear Project Brief                               │
│      └─> Documentar hallazgos                              │
│      └─> Preparar recomendaciones                          │
│                                                             │
│   SALIDA: docs/1-analysis/project-brief.md                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              [Siguiente: FASE DEFINIR]
```

## Checklist de Entregables

- [ ] Tipo de proyecto identificado (greenfield/brownfield)
- [ ] Escala del proyecto determinada (quick/standard/enterprise)
- [ ] Project Brief creado
- [ ] User Personas definidas
- [ ] Analisis de mercado completado (si aplica)
- [ ] Problema claramente definido
- [ ] Solucion de alto nivel propuesta

## Integraciones

### Con Gemini (nxt-search)
Usar para:
- Investigacion de mercado actual
- Analisis de competidores
- Tendencias de la industria
- Verificacion de hechos

```bash
python herramientas/gemini_tools.py search "mercado [industria] 2025"
python herramientas/gemini_tools.py current "tendencias [tecnologia]"
```

## Artefactos Generados

| Artefacto | Ubicacion | Formato |
|-----------|-----------|---------|
| Project Brief | `docs/1-analysis/project-brief.md` | Markdown |
| Market Research | `docs/1-analysis/market-research.md` | Markdown |
| User Personas | `docs/1-analysis/user-personas.md` | Markdown |
| Competitive Analysis | `docs/1-analysis/competitive-analysis.md` | Markdown |

## Criterios de Salida

Para pasar a la siguiente fase (DEFINIR):

1. Project Brief aprobado
2. Problema claramente entendido
3. Usuarios objetivo identificados
4. Viabilidad inicial validada

## Siguiente Paso

```
Al completar esta fase, ejecuta:
/nxt/pm

Esto activara el agente PM para crear el PRD en la fase DEFINIR.
```
