# VER ESTADO DEL PROYECTO - EJECUCION DIRECTA

**INSTRUCCION:** Muestra el estado del sistema NXT.

## PASO 1: Estado del orquestador
Ejecuta con Bash:
```bash
python herramientas/nxt_orchestrator_v3.py status
```

## PASO 2: Estado de git
Ejecuta con Bash:
```bash
git status --short
```

## PASO 3: Estado de Telemetria
Ejecuta con Bash:
```bash
if [ -f ".env" ] && grep -q "NXT_SUPABASE" .env 2>/dev/null; then
  echo "Telemetria: CENTRALIZADA (Supabase)"
else
  echo "Telemetria: LOCAL ONLY (.nxt/telemetry.jsonl)"
fi
echo "Eventos registrados: $(wc -l < .nxt/telemetry.jsonl 2>/dev/null || echo 0)"
```

## PASO 4: Estado del Proyecto
Lee `.nxt/state.json` y muestra:
- Tarea actual: `current_context.task`
- Fase: `current_context.current_phase`
- Pasos pendientes: `current_context.pending_steps`
- Tareas pendientes: cantidad en `pending_tasks`
- Última actividad: `last_updated`

## PASO 5: Resumen
Muestra resumen de agentes, skills y workflows disponibles.

**NO PREGUNTES. EJECUTA.**
