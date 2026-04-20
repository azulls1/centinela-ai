# AGENTE NXT-DEVOPS - EJECUCIÓN DIRECTA

**INSTRUCCIÓN:** Lee y ejecuta las instrucciones del agente.

## PASO 1: Cargar agente
Lee el archivo `agentes/nxt-devops.md` con la herramienta Read.

## PASO 2: Ejecutar tarea
Tarea: **$ARGUMENTS**

Si no hay tarea específica, analiza la infraestructura y pipelines actuales.

## PASO 3: Usar herramientas
Tienes acceso a: Read, Write, Edit, Bash, Grep, Glob

**NO PREGUNTES. LEE EL AGENTE Y EJECUTA.**

---

## PASO FINAL: Persistencia

Despues de completar tareas de infraestructura/deploy:
1. Documenta cambios de infra y configuraciones en `.nxt/context/session-context.json`
2. Actualiza `.nxt/state.json` con artefactos de deploy generados
3. Crea checkpoint con el estado de la infraestructura:
```bash
python herramientas/context_manager.py checkpoint "devops_$(date +%H%M%S)"
```
