# GUARDAR CHECKPOINT - EJECUCIÓN DIRECTA

**INSTRUCCIÓN:** Guarda el estado actual del proyecto.

## PASO 1: Crear directorio
Asegura que existe `.nxt/checkpoints/`

## PASO 2: Guardar estado
Crea archivo JSON en `.nxt/checkpoints/checkpoint_[timestamp].json` con:
```json
{
  "timestamp": "ISO datetime",
  "task": "descripción de la tarea actual",
  "decisions": ["lista de decisiones tomadas"],
  "files_modified": ["lista de archivos modificados"],
  "next_step": "siguiente paso a ejecutar",
  "context": "contexto relevante para continuar"
}
```

## PASO 3: Confirmar
Muestra mensaje de confirmación con ruta del checkpoint.

**NO PREGUNTES. EJECUTA.**
