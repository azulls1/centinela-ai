# SKILL: Context Persistence

> **Version:** 3.8.0
> **Trigger:** Persistencia y recuperacion de contexto de sesion
> **Agente:** nxt-context, nxt-multicontext
> **Track:** shared

## Descripcion

Skill para persistir y recuperar estado del sistema NXT, previniendo perdida de contexto en sesiones largas.

---

## Problema que Resuelve

```
ANTES (sin persistencia)              DESPUES (con persistencia)
─────────────────────────             ─────────────────────────
Contexto lleno                        Contexto lleno
      │                                     │
      ▼                                     ▼
Compactacion                          Checkpoint guardado
      │                                     │
      ▼                                     ▼
❌ Estado perdido                     ✅ Estado recuperable
❌ Decisiones olvidadas               ✅ Decisiones preservadas
❌ Comportamiento erratico            ✅ Continuidad garantizada
```

---

## Capacidades

### 1. Checkpoint Management
- Crear checkpoints automaticos
- Checkpoints manuales bajo demanda
- Rotacion de checkpoints (mantener N ultimos)
- Validacion de integridad

### 2. State Serialization
- Serializar estado del orquestador
- Serializar estado de agentes
- Serializar decisiones y artefactos
- Formato JSON compacto

### 3. Recovery
- Detectar necesidad de recovery
- Cargar ultimo checkpoint valido
- Validar estado cargado
- Reconstruir contexto

### 4. Summarization
- Crear resumenes estructurados
- Preservar informacion critica
- Formato recuperable

---

## Estructura de Estado

### Estado Completo

```json
{
  "version": "1.0.0",
  "checkpoint_id": "cp_20250120_143500",
  "timestamp": "2025-01-20T14:35:00Z",

  "orchestrator": {
    "active": true,
    "task": {
      "id": "task_001",
      "description": "Implementar OAuth2",
      "classification": "level_3",
      "started_at": "2025-01-20T14:00:00Z"
    },
    "workflow": {
      "phase": "construir",
      "step": 3,
      "total_steps": 8
    }
  },

  "agents": {
    "history": ["analyst", "pm", "architect"],
    "current": "api",
    "pending": ["cybersec", "qa"]
  },

  "decisions": [
    {
      "key": "auth_method",
      "value": "JWT",
      "context": "Stateless API"
    }
  ],

  "artifacts": {
    "created": ["file1.ts", "file2.ts"],
    "modified": ["config.ts"],
    "pending": ["guard.ts"]
  },

  "user_preferences": {
    "typescript_strict": true,
    "test_style": "integration"
  }
}
```

### Estado Minimo (para recovery rapido)

```json
{
  "task": "Implementar OAuth2",
  "progress": "37.5%",
  "current_agent": "api",
  "next_action": "Crear auth.guard.ts",
  "key_decisions": ["JWT", "jose", "Google+GitHub"],
  "files_created": ["jwt.service.ts", "oauth.controller.ts"]
}
```

---

## Triggers de Checkpoint

| Trigger | Prioridad | Estado Guardado |
|---------|-----------|-----------------|
| `on_task_start` | Alta | Completo |
| `on_agent_switch` | Alta | Completo |
| `on_step_complete` | Media | Completo |
| `on_decision` | Media | Incremental |
| `on_file_create` | Baja | Incremental |
| `on_interval` | Media | Completo |
| `on_context_warning` | Critica | Completo + Summary |

---

## Formato de Archivos

### Checkpoint File

```
.nxt/state/checkpoints/cp_YYYYMMDD_HHMMSS.json
```

### Session File

```
.nxt/state/sessions/session_YYYYMMDD.json
```

### Recovery File

```
.nxt/state/recovery/last_known_good.json
```

---

## API del Skill

### Crear Checkpoint

```python
def create_checkpoint(
    trigger: str,
    state: dict,
    summary: str = None
) -> str:
    """
    Crea un checkpoint del estado actual.

    Args:
        trigger: Que disparo el checkpoint
        state: Estado completo a guardar
        summary: Resumen opcional

    Returns:
        checkpoint_id: ID del checkpoint creado
    """
```

### Cargar Checkpoint

```python
def load_checkpoint(
    checkpoint_id: str = None
) -> dict:
    """
    Carga un checkpoint.

    Args:
        checkpoint_id: ID especifico o None para el ultimo

    Returns:
        state: Estado cargado
    """
```

### Validar Estado

```python
def validate_state(state: dict) -> bool:
    """
    Valida que un estado sea consistente.

    Returns:
        True si el estado es valido
    """
```

### Crear Resumen

```python
def create_summary(state: dict) -> str:
    """
    Crea un resumen estructurado del estado.

    Returns:
        Markdown con resumen recuperable
    """
```

---

## Integracion con MCP Memory

```python
# Si MCP Memory esta disponible
if mcp_memory.is_available():
    # Guardar en MCP ademas de archivo
    mcp_memory.store(
        key=f"nxt_checkpoint_{checkpoint_id}",
        value=state,
        ttl=86400 * 7  # 7 dias
    )
```

---

## Ejemplo de Uso

### Guardar Estado

```python
# En el orquestador
from skills.context_persistence import create_checkpoint

# Despues de cambiar de agente
state = orchestrator.get_full_state()
checkpoint_id = create_checkpoint(
    trigger="on_agent_switch",
    state=state,
    summary=f"Cambiando de {old_agent} a {new_agent}"
)
print(f"Checkpoint creado: {checkpoint_id}")
```

### Recuperar Estado

```python
from skills.context_persistence import load_checkpoint, validate_state

# Al detectar perdida de contexto
state = load_checkpoint()  # carga el ultimo

if validate_state(state):
    orchestrator.restore_state(state)
    print("Estado recuperado exitosamente")
else:
    # Intentar checkpoint anterior
    state = load_checkpoint(checkpoint_id="cp_20250120_143000")
```

---

## Checklist de Persistencia

### Que SIEMPRE persistir
- [ ] Tarea actual y su clasificacion
- [ ] Fase y paso del workflow
- [ ] Agente activo
- [ ] Decisiones tomadas
- [ ] Archivos creados/modificados

### Que persistir si hay espacio
- [ ] Contexto del usuario
- [ ] Historial de agentes
- [ ] Mensajes importantes
- [ ] Errores encontrados

### Que NO persistir
- [ ] Contenido completo de archivos (solo paths)
- [ ] Logs verbosos
- [ ] Estados intermedios no importantes

---

## Configuracion

```yaml
# .nxt/persistence.config.yaml
persistence:
  enabled: true

  checkpoints:
    max_count: 20
    auto_interval: 300  # 5 min
    on_agent_switch: true
    on_decision: true

  storage:
    local: true
    mcp_memory: true

  compression: false
  encryption: false
```

---

## Implementacion Real

### Crear Checkpoint (Python)
```python
import json
from pathlib import Path
from datetime import datetime

def create_checkpoint(root: Path, description: str = "") -> str:
    """Crea un checkpoint del estado actual."""
    cp_dir = root / ".nxt" / "checkpoints"
    cp_dir.mkdir(parents=True, exist_ok=True)

    # Leer estado actual
    state = {}
    state_file = root / ".nxt" / "state.json"
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))

    # Crear checkpoint
    cp_id = f"cp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    checkpoint = {
        "checkpoint_id": cp_id,
        "timestamp": datetime.now().isoformat(),
        "description": description,
        "state": state,
        "recovery_instructions": [
            f"Estado guardado: {state.get('current_phase', 'unknown')}",
            f"Tareas pendientes: {len(state.get('pending_tasks', []))}",
        ]
    }

    cp_file = cp_dir / f"{cp_id}.json"
    cp_file.write_text(json.dumps(checkpoint, indent=2, ensure_ascii=False), encoding="utf-8")
    return cp_id

def load_checkpoint(root: Path, cp_id: str = None) -> dict:
    """Carga el checkpoint mas reciente o uno especifico."""
    cp_dir = root / ".nxt" / "checkpoints"
    if cp_id:
        cp_file = cp_dir / f"{cp_id}.json"
    else:
        # Mas reciente
        files = sorted(cp_dir.glob("cp_*.json"), reverse=True)
        cp_file = files[0] if files else None

    if cp_file and cp_file.exists():
        return json.loads(cp_file.read_text(encoding="utf-8"))
    return {}
```

### Decision Tree: Cuando Crear Checkpoint?
```
Crear checkpoint ahora?
├── Acabas de tomar una decision arquitectonica? --> SI
├── Vas a cambiar de agente? --> SI
├── Completaste un paso del workflow? --> SI
├── La sesion lleva mas de 30 minutos? --> SI (checkpoint periodico)
├── Solo leiste archivos sin cambiar nada? --> NO
├── El cambio fue trivial (typo, format)? --> NO
```

---

*SKILL Context Persistence v1.0.0 - Persistencia de estado para continuidad*
