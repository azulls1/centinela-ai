# AGENTE NXT-DEV - EJECUCIÓN DIRECTA

**INSTRUCCIÓN:** Lee y ejecuta las instrucciones del agente.

## PASO 1: Cargar agente
Lee el archivo `agentes/nxt-dev.md` con la herramienta Read.

## PASO 2: Ejecutar tarea
Tarea: **$ARGUMENTS**

Si no hay tarea específica, analiza el proyecto y ejecuta la mejora más prioritaria.

## PASO 3: Usar herramientas
Tienes acceso a: Read, Write, Edit, Bash, Grep, Glob

**NO PREGUNTES. LEE EL AGENTE Y EJECUTA.**

---

## PASO FINAL: Persistencia

Despues de completar el desarrollo:
1. Si creaste archivos nuevos, actualiza artifacts en `.nxt/state.json`
2. Si la tarea esta completa, muevela a completed_tasks en `.nxt/state.json`
3. Si tomaste decisiones tecnicas, documenta en `.nxt/context/session-context.json`
4. Crea checkpoint si los cambios fueron significativos:
```bash
python herramientas/context_manager.py checkpoint "dev_$(date +%H%M%S)"
```
