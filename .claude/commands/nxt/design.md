# AGENTE NXT-DESIGN - EJECUCION DIRECTA

**INSTRUCCION:** Lee y ejecuta las instrucciones del agente.

## PASO 1: Cargar agente
Lee el archivo `agentes/nxt-design.md` con la herramienta Read.

## PASO 2: Ejecutar tarea
Tarea: **$ARGUMENTS**

Si no hay tarea especifica:
- Analiza la UI/UX actual del proyecto
- Revisa el design system existente
- Propone mejoras de experiencia y componentes
- Verifica accesibilidad basica

## PASO 3: Usar herramientas
Tienes acceso a: Read, Write, Edit, Bash, Grep, Glob

## Capacidades del agente fusionado:
- **UX Research:** Personas, journey maps, user flows
- **UI Design:** Wireframes, mockups, design system
- **Implementation:** Componentes React/Vue, responsive, a11y
- **Performance:** Core Web Vitals, optimizacion frontend

**NO PREGUNTES. LEE EL AGENTE Y EJECUTA.**

---

## PASO FINAL: Persistencia

Despues de completar el diseno:
1. Documenta decisiones de UX/UI en `.nxt/context/session-context.json`
2. Si creaste componentes o archivos, actualiza artifacts en `.nxt/state.json`
3. Crea checkpoint con el progreso:
```bash
python herramientas/context_manager.py checkpoint "design_$(date +%H%M%S)"
```
