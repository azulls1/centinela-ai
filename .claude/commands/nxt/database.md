# AGENTE NXT-DATABASE - EJECUCIÓN DIRECTA

**INSTRUCCIÓN:** Lee y ejecuta las instrucciones del agente.

## PASO 1: Cargar agente
Lee el archivo `agentes/nxt-database.md` con la herramienta Read.

## PASO 2: Ejecutar tarea
Tarea: **$ARGUMENTS**

Si no hay tarea específica, analiza el schema actual y propone optimizaciones.

## PASO 3: Usar herramientas
Tienes acceso a: Read, Write, Edit, Bash, Grep, Glob

**NO PREGUNTES. LEE EL AGENTE Y EJECUTA.**

---

## PASO FINAL: Persistencia

Despues de completar cambios de base de datos:
1. Documenta cambios de schema en `.nxt/context/session-context.json`
2. Si creaste migraciones, actualiza artifacts en `.nxt/state.json`
3. Crea checkpoint con los cambios de DB:
```bash
python herramientas/context_manager.py checkpoint "database_$(date +%H%M%S)"
```
