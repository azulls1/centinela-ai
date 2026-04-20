# NXT ORCHESTRATOR - EJECUCIÓN AUTÓNOMA DIRECTA

**INSTRUCCIÓN PARA CLAUDE: Ejecuta estos pasos EN ORDEN, sin preguntar.**

---

## PASO 1: ANÁLISIS DEL PROYECTO

Ejecuta con Bash:
```bash
python herramientas/nxt_orchestrator_v3.py analyze
```

---

## PASO 2: LEER ARCHIVOS DEL PROYECTO

Lee en paralelo (usa Read tool):
- `package.json` (si existe)
- `requirements.txt` o `pyproject.toml` (si existe)
- `README.md`
- `CLAUDE.md`

---

## PASO 3: BUSCAR TAREAS PENDIENTES

Usa Grep para buscar:
```
TODO:|FIXME:|HACK:|XXX:
```

---

## PASO 4: Ejecutar Agentes (EN ORDEN)

Consulta `.nxt/task-routing.yaml` para determinar el tipo de tarea:
1. Lee `.nxt/task-routing.yaml` con Read tool
2. Busca en `task_routing` el tipo que mejor match (bug_fix, api_endpoint, full_feature, etc.)
3. Usa los `agents` y `order` de ese tipo
4. Aplica `conditions` si corresponden (e.g., si toca auth → agregar cybersec)

Para cada agente en el plan, en orden:
1. Lee el archivo del agente: `agentes/nxt-[agente].md`
2. Ejecuta las instrucciones del agente para la tarea
3. Reporta resultado: "✓ [agente] completado"
4. Continua con el siguiente agente

Ejecuta las acciones con las herramientas disponibles (Read, Write, Edit, Bash, Grep, Glob).

**Agentes disponibles (33):**
- nxt-analyst, nxt-pm, nxt-architect, nxt-design
- nxt-dev, nxt-qa, nxt-edge-case-hunter, nxt-devops, nxt-cybersec
- nxt-docs, nxt-api, nxt-database
- nxt-scrum, nxt-infra, nxt-search, nxt-media
- nxt-integrations, nxt-flows, nxt-migrator
- nxt-performance, nxt-accessibility, nxt-mobile
- nxt-data, nxt-aiml, nxt-compliance, nxt-realtime
- nxt-localization, nxt-paige, nxt-context
- nxt-changelog, nxt-ralph, nxt-multicontext

---

## PASO 5: Resumen Final

Muestra:
- Agentes ejecutados y resultados
- Archivos creados/modificados
- Decisiones tomadas
- Siguiente paso recomendado

```
╔══════════════════════════════════════════════════════════════════╗
║   🎯 NXT ORCHESTRATOR - Ejecución Completada                     ║
╚══════════════════════════════════════════════════════════════════╝

📊 ANÁLISIS
[resumen del proyecto]

🤖 AGENTES EJECUTADOS
[lista de agentes y resultado: ✓ completado / ✗ error]

📋 ARCHIVOS CREADOS/MODIFICADOS
[lista de archivos con accion: creado/modificado/eliminado]

🧠 DECISIONES TOMADAS
[decisiones arquitectonicas o de diseno relevantes]

🎯 SIGUIENTE PASO RECOMENDADO
[recomendación]
```

---

## REGLAS

1. **NO PREGUNTES** - Actúa directamente
2. **USA LAS HERRAMIENTAS** - Read, Write, Edit, Bash, Grep, Glob
3. **LEE LOS AGENTES** - Cada agente tiene instrucciones específicas
4. **EJECUTA TODO** - No te detengas a pedir confirmación

---

**$ARGUMENTS** = Tarea específica del usuario (si la hay)

Si hay argumentos, enfócate en esa tarea.
Si no hay argumentos, analiza el proyecto y ejecuta las mejoras prioritarias.

---

## PASO FINAL: Persistencia

Despues de ejecutar el plan:
1. Actualiza `.nxt/state.json` con el progreso (tareas completadas, fase actual, decisiones)
2. Si hubo decisiones arquitectonicas o de diseno, documenta en `.nxt/context/session-context.json`
3. Crea checkpoint si hubo cambios significativos:
```bash
python herramientas/context_manager.py checkpoint "orchestrator_$(date +%H%M%S)"
```

---

**COMIENZA AHORA CON EL PASO 1.**
