# AGENTE NXT-QA - EJECUCIÓN DIRECTA

**INSTRUCCIÓN:** Lee y ejecuta las instrucciones del agente.

## PASO 1: Cargar agente
Lee el archivo `agentes/nxt-qa.md` con la herramienta Read.

## PASO 2: Ejecutar tarea
Tarea: **$ARGUMENTS**

Si no hay tarea específica, ejecuta tests y validación del proyecto.

## PASO 3: Usar herramientas
Tienes acceso a: Read, Write, Edit, Bash, Grep, Glob

**NO PREGUNTES. LEE EL AGENTE Y EJECUTA.**

---

## PASO FINAL: Persistencia

Despues de completar la verificacion:
1. Actualiza `.nxt/state.json` con resultados de QA (tests pasados, issues encontrados)
2. Si encontraste bugs o issues, agregalos a pending_tasks en `.nxt/state.json`
3. Si la verificacion completa una tarea, muevela a completed_tasks
4. Crea checkpoint con resultados:
```bash
python herramientas/context_manager.py checkpoint "qa_$(date +%H%M%S)"
```
