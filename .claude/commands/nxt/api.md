# AGENTE NXT-API - EJECUCIÓN DIRECTA

**INSTRUCCIÓN:** Lee y ejecuta las instrucciones del agente.

## PASO 1: Cargar agente
Lee el archivo `agentes/nxt-api.md` con la herramienta Read.

## PASO 2: Ejecutar tarea
Tarea: **$ARGUMENTS**

Si no hay tarea específica, analiza las APIs existentes y propone mejoras.

## PASO 3: Usar herramientas
Tienes acceso a: Read, Write, Edit, Bash, Grep, Glob

**NO PREGUNTES. LEE EL AGENTE Y EJECUTA.**

---

## PASO FINAL: Persistencia

Despues de completar el desarrollo de APIs:
1. Si creaste endpoints nuevos, actualiza artifacts en `.nxt/state.json`
2. Si la tarea esta completa, muevela a completed_tasks en `.nxt/state.json`
3. Documenta decisiones de API design en `.nxt/context/session-context.json`
4. Crea checkpoint si los cambios fueron significativos:
```bash
python herramientas/context_manager.py checkpoint "api_$(date +%H%M%S)"
```
