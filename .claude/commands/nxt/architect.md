# AGENTE NXT-ARCHITECT - EJECUCIÓN DIRECTA

**INSTRUCCIÓN:** Lee y ejecuta las instrucciones del agente.

## PASO 1: Cargar agente
Lee el archivo `agentes/nxt-architect.md` con la herramienta Read.

## PASO 2: Ejecutar tarea
Tarea: **$ARGUMENTS**

Si no hay tarea específica, analiza la arquitectura actual y propone mejoras.

## PASO 3: Usar herramientas
Tienes acceso a: Read, Write, Edit, Bash, Grep, Glob

**NO PREGUNTES. LEE EL AGENTE Y EJECUTA.**

---

## PASO FINAL: Persistencia

Despues de completar el diseno arquitectonico:
1. Documenta decisiones arquitectonicas (ADRs) en `.nxt/context/session-context.json`
2. Actualiza `.nxt/state.json` con artefactos generados y fase actual
3. Crea checkpoint con la arquitectura propuesta:
```bash
python herramientas/context_manager.py checkpoint "architect_$(date +%H%M%S)"
```
