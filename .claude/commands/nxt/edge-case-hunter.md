# AGENTE NXT-EDGE-CASE-HUNTER - EJECUCIÓN DIRECTA

**INSTRUCCIÓN:** Lee y ejecuta las instrucciones del agente.

## PASO 1: Cargar agente
Lee el archivo `agentes/nxt-edge-case-hunter.md` con la herramienta Read.

## PASO 2: Identificar cambios
Tarea: **$ARGUMENTS**

Si hay argumentos, revisar esos archivos especificos.
Si no hay argumentos, identificar archivos modificados recientemente con git:
```bash
git diff --name-only HEAD~1
```

## PASO 3: Ejecutar Review Adversarial
Para CADA archivo modificado:
1. Leer el archivo completo con Read tool
2. Trazar CADA branching path (if/else/switch/try-catch/ternary)
3. Verificar boundary conditions de CADA input
4. Para codigo async, verificar error handling completo
5. Documentar gaps encontrados con severidad

## PASO 4: Usar herramientas
Tienes acceso a: Read, Write, Edit, Bash, Grep, Glob

## PASO 5: Generar Reporte
Crear `docs/4-implementation/edge-case-review.md` con Write tool.
Si no hay gaps, crear el archivo igualmente indicando "no gaps encontrados".

**NO PREGUNTES. LEE EL AGENTE Y EJECUTA.**

---

## PASO FINAL: Persistencia

Despues de completar la revision:
1. Actualiza `.nxt/state.json` con resultados del edge case hunting (gaps encontrados, archivos analizados)
2. Si encontraste edge cases criticos, agregalos a pending_tasks en `.nxt/state.json`
3. Si la revision completa una tarea, muevela a completed_tasks
4. Crea checkpoint con resultados:
```bash
python herramientas/context_manager.py checkpoint "edge_case_$(date +%H%M%S)"
```
