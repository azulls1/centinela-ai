# NXT RESUME - Recuperar Contexto

**INSTRUCCION:** Ejecuta estos pasos EN ORDEN para recuperar el contexto de trabajo.

---

## PASO 1: Cargar Estado

Lee el archivo `.nxt/state.json` con la herramienta Read para entender:
- Tarea actual (`current_context.task`)
- Fase actual (`current_context.current_phase`)
- Pasos completados y pendientes
- Decisiones tomadas

---

## PASO 2: Cargar Contexto de Sesion

Lee `.nxt/context/session-context.json` con la herramienta Read para recuperar:
- ADRs (decisiones arquitectonicas)
- Patrones de codigo del proyecto
- Preferencias aprendidas
- Artefactos generados

---

## PASO 3: Buscar Ultimo Checkpoint

Ejecuta con Bash:
```bash
mkdir -p .nxt/checkpoints 2>/dev/null
python herramientas/context_manager.py status 2>&1 || echo "Context manager no disponible - usando archivos directamente"
```

Busca checkpoints disponibles:
```bash
ls -lt .nxt/checkpoints/*.json 2>/dev/null | head -5 || echo "No hay checkpoints guardados"
```

Si hay checkpoints, lee el mas reciente para obtener contexto adicional.
Si NO hay checkpoints, usa solo state.json y session-context.json (pasos 1-2).

---

## PASO 4: Mostrar Resumen

Muestra al usuario un resumen claro:
```
==================================================================
  NXT RESUME - Contexto Recuperado
==================================================================

TAREA ACTUAL
[nombre de la tarea en la que se estaba trabajando]

FASE
[fase actual y progreso]

DECISIONES CLAVE
[lista de decisiones importantes tomadas]

ARTEFACTOS GENERADOS
[archivos creados/modificados]

SIGUIENTE PASO
[paso pendiente recomendado]
==================================================================
```

---

## PASO 5: Continuar

Indica al usuario: "Contexto recuperado. El siguiente paso es [paso pendiente]. Continuando..."

Si hay una tarea clara pendiente, continua ejecutandola automaticamente.

---

**NO PREGUNTES. CARGA EL CONTEXTO Y MUESTRA EL RESUMEN.**
