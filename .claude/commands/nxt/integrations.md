# AGENTE NXT-INTEGRATIONS - EJECUCIÓN DIRECTA

**INSTRUCCIÓN:** Lee y ejecuta las instrucciones del agente.

## PASO 1: Cargar agente
Lee el archivo `agentes/nxt-integrations.md` con la herramienta Read.

## PASO 2: Ejecutar tarea
Tarea: **$ARGUMENTS**

Si no hay tarea específica, analiza las integraciones existentes.

## PASO 3: Usar herramientas
Tienes acceso a: Read, Write, Edit, Bash, Grep, Glob

**NO PREGUNTES. LEE EL AGENTE Y EJECUTA.**

## PASO FINAL: Persistencia
Despues de completar la tarea:
1. Si tomaste decisiones importantes, actualiza `.nxt/context/session-context.json`
2. Si la tarea se completo, actualiza `.nxt/state.json` (mover a completed_tasks)
3. Si hubo cambios significativos de codigo, crea checkpoint:
   `python herramientas/context_manager.py checkpoint "integrations_$(date +%H%M%S)"`
