# AGENTE NXT-CYBERSEC - EJECUCIÓN DIRECTA

**INSTRUCCIÓN:** Lee y ejecuta las instrucciones del agente.

## PASO 1: Cargar agente
Lee el archivo `agentes/nxt-cybersec.md` con la herramienta Read.

## PASO 2: Ejecutar tarea
Tarea: **$ARGUMENTS**

Si no hay tarea específica, ejecuta auditoría de seguridad OWASP.

## PASO 3: Usar herramientas
Tienes acceso a: Read, Write, Edit, Bash, Grep, Glob

**NO PREGUNTES. LEE EL AGENTE Y EJECUTA.**

---

## PASO FINAL: Persistencia

Despues de completar la auditoria de seguridad:
1. Documenta vulnerabilidades encontradas y remediaciones en `.nxt/context/session-context.json`
2. Si hay issues de seguridad pendientes, agregalos a pending_tasks en `.nxt/state.json`
3. Crea checkpoint con resultados de seguridad:
```bash
python herramientas/context_manager.py checkpoint "cybersec_$(date +%H%M%S)"
```
