# NXT Persistence Steps (include in every command)

## PASO FINAL: Persistencia Automatica
Despues de completar la tarea, ejecuta estos pasos de persistencia:

### Guardar Contexto
Si tomaste decisiones importantes o aprendiste algo del proyecto:
- Actualiza `.nxt/context/session-context.json` con decisiones nuevas
- Agrega ADRs si hubo decisiones arquitectonicas

### Checkpoint (si hubo cambios significativos)
Si creaste/modificaste archivos de codigo:
```bash
python herramientas/context_manager.py checkpoint "$(date +%Y%m%d_%H%M%S)"
```

### Estado
Actualiza `.nxt/state.json` si:
- Se completo una tarea pendiente -> mover a completed_tasks
- Se cambio de fase -> actualizar current_phase
- Se tomo una decision -> agregar a decisions_log
