#!/usr/bin/env python3
"""
NXT AI Development - Event Bus
==============================
Sistema de eventos pub/sub para comunicación entre componentes.

Características:
- Publicación y suscripción de eventos
- Eventos tipados
- Callbacks asíncronos
- Historial de eventos
- Filtros de eventos

Versión: 3.8.0
"""

import json
from datetime import datetime
from typing import Callable, Dict, Any, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict
import threading
import queue


class EventType(Enum):
    """Tipos de eventos del sistema."""
    # Lifecycle events
    SYSTEM_INIT = "system.init"
    SYSTEM_SHUTDOWN = "system.shutdown"

    # Orchestrator events
    TASK_CLASSIFIED = "orchestrator.task_classified"
    TASK_PLANNED = "orchestrator.task_planned"
    TASK_STARTED = "orchestrator.task_started"
    TASK_COMPLETED = "orchestrator.task_completed"
    TASK_FAILED = "orchestrator.task_failed"
    TASK_DELEGATED = "orchestrator.task_delegated"

    # Agent events
    AGENT_ACTIVATED = "agent.activated"
    AGENT_DEACTIVATED = "agent.deactivated"
    AGENT_DELEGATED = "agent.delegated"
    AGENT_COMPLETED = "agent.completed"
    AGENT_ERROR = "agent.error"
    AGENT_COMMUNICATION = "agent.communication"

    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_STEP_STARTED = "workflow.step_started"
    WORKFLOW_STEP_COMPLETED = "workflow.step_completed"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

    # Parallel execution events (v3.3.0)
    PARALLEL_STARTED = "parallel.started"
    PARALLEL_TASK_STARTED = "parallel.task_started"
    PARALLEL_TASK_COMPLETED = "parallel.task_completed"
    PARALLEL_LEVEL_COMPLETED = "parallel.level_completed"
    PARALLEL_COMPLETED = "parallel.completed"
    PARALLEL_FAILED = "parallel.failed"

    # Skill events
    SKILL_LOADED = "skill.loaded"
    SKILL_INVOKED = "skill.invoked"
    SKILL_COMPLETED = "skill.completed"

    # MCP events
    MCP_SERVER_ENABLED = "mcp.server_enabled"
    MCP_SERVER_DISABLED = "mcp.server_disabled"
    MCP_CALL_STARTED = "mcp.call_started"
    MCP_CALL_COMPLETED = "mcp.call_completed"

    # Hook events
    HOOK_TRIGGERED = "hook.triggered"
    HOOK_COMPLETED = "hook.completed"
    HOOK_FAILED = "hook.failed"

    # State events
    STATE_UPDATED = "state.updated"
    DECISION_LOGGED = "state.decision_logged"

    # Context events (v3.3.0)
    CHECKPOINT_CREATED = "context.checkpoint_created"
    CHECKPOINT_RESTORED = "context.checkpoint_restored"
    CONTEXT_COMPACTED = "context.compacted"
    CONTEXT_RECOVERED = "context.recovered"

    # Integration Hub events (v3.3.0)
    HUB_MESSAGE = "hub.message"
    HUB_BROADCAST = "hub.broadcast"
    HUB_REQUEST = "hub.request"
    HUB_RESPONSE = "hub.response"

    # Custom events
    CUSTOM = "custom"


@dataclass
class Event:
    """Representa un evento del sistema."""
    type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    id: str = field(default_factory=lambda: f"evt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario."""
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp
        }

    def to_json(self) -> str:
        """Convierte el evento a JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Crea un evento desde diccionario."""
        return cls(
            type=EventType(data["type"]),
            data=data.get("data", {}),
            source=data.get("source", "unknown"),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            id=data.get("id", f"evt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
        )


class EventSubscription:
    """Representa una suscripción a eventos."""

    def __init__(self, event_type: EventType, callback: Callable[[Event], None],
                 filter_fn: Callable[[Event], bool] = None,
                 once: bool = False):
        self.event_type = event_type
        self.callback = callback
        self.filter_fn = filter_fn
        self.once = once
        self.id = f"sub_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    def matches(self, event: Event) -> bool:
        """Verifica si el evento coincide con la suscripción."""
        if event.type != self.event_type:
            return False
        if self.filter_fn and not self.filter_fn(event):
            return False
        return True


class EventBus:
    """
    Bus de eventos central para el sistema NXT.

    Permite publicación y suscripción de eventos entre componentes.
    """

    def __init__(self, max_history: int = 1000):
        """
        Inicializa el event bus.

        Args:
            max_history: Número máximo de eventos a mantener en historial
        """
        self._subscriptions: Dict[EventType, List[EventSubscription]] = defaultdict(list)
        self._history: List[Event] = []
        self._max_history = max_history
        self._lock = threading.Lock()
        self._async_queue = queue.Queue()
        self._running = True

    def subscribe(self, event_type: EventType,
                  callback: Callable[[Event], None],
                  filter_fn: Callable[[Event], bool] = None,
                  once: bool = False) -> str:
        """
        Suscribe a un tipo de evento.

        Args:
            event_type: Tipo de evento a escuchar
            callback: Función a llamar cuando ocurra el evento
            filter_fn: Función opcional para filtrar eventos
            once: Si True, la suscripción se elimina después del primer evento

        Returns:
            ID de la suscripción
        """
        subscription = EventSubscription(event_type, callback, filter_fn, once)
        with self._lock:
            self._subscriptions[event_type].append(subscription)
        return subscription.id

    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Cancela una suscripción.

        Args:
            subscription_id: ID de la suscripción a cancelar

        Returns:
            True si se encontró y eliminó
        """
        with self._lock:
            for event_type, subs in self._subscriptions.items():
                for sub in subs:
                    if sub.id == subscription_id:
                        subs.remove(sub)
                        return True
        return False

    def publish(self, event: Event) -> int:
        """
        Publica un evento.

        Args:
            event: Evento a publicar

        Returns:
            Número de suscriptores notificados
        """
        with self._lock:
            # Agregar a historial
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history.pop(0)

            # Obtener suscriptores
            subscriptions = self._subscriptions.get(event.type, []).copy()

        # Notificar suscriptores
        notified = 0
        to_remove = []

        for sub in subscriptions:
            if sub.matches(event):
                try:
                    sub.callback(event)
                    notified += 1
                    if sub.once:
                        to_remove.append(sub.id)
                except Exception as e:
                    # Log error but continue
                    print(f"Error in event subscriber: {e}")

        # Eliminar suscripciones "once"
        for sub_id in to_remove:
            self.unsubscribe(sub_id)

        return notified

    def emit(self, event_type: EventType, data: Dict[str, Any] = None,
             source: str = "system") -> Event:
        """
        Emite un nuevo evento (shortcut para crear y publicar).

        Args:
            event_type: Tipo de evento
            data: Datos del evento
            source: Fuente del evento

        Returns:
            El evento emitido
        """
        event = Event(
            type=event_type,
            data=data or {},
            source=source
        )
        self.publish(event)
        return event

    def get_history(self, event_type: EventType = None,
                    limit: int = 100) -> List[Event]:
        """
        Obtiene el historial de eventos.

        Args:
            event_type: Filtrar por tipo (opcional)
            limit: Número máximo de eventos

        Returns:
            Lista de eventos
        """
        with self._lock:
            if event_type:
                filtered = [e for e in self._history if e.type == event_type]
            else:
                filtered = self._history.copy()

            return filtered[-limit:]

    def clear_history(self):
        """Limpia el historial de eventos."""
        with self._lock:
            self._history.clear()

    def get_subscription_count(self, event_type: EventType = None) -> int:
        """
        Obtiene el número de suscripciones.

        Args:
            event_type: Tipo específico (opcional)

        Returns:
            Número de suscripciones
        """
        with self._lock:
            if event_type:
                return len(self._subscriptions.get(event_type, []))
            return sum(len(subs) for subs in self._subscriptions.values())

    def on(self, event_type: EventType):
        """
        Decorador para suscribirse a eventos.

        Usage:
            @bus.on(EventType.TASK_COMPLETED)
            def handle_task_completed(event):
                print(event.data)
        """
        def decorator(fn):
            self.subscribe(event_type, fn)
            return fn
        return decorator

    def once(self, event_type: EventType):
        """
        Decorador para suscripción de una sola vez.

        Usage:
            @bus.once(EventType.SYSTEM_INIT)
            def handle_init(event):
                print("System initialized!")
        """
        def decorator(fn):
            self.subscribe(event_type, fn, once=True)
            return fn
        return decorator


# =============================================================================
# GLOBAL EVENT BUS INSTANCE
# =============================================================================

_global_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Obtiene la instancia global del event bus."""
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus


def emit(event_type: EventType, data: Dict[str, Any] = None,
         source: str = "system") -> Event:
    """Emite un evento usando el bus global."""
    return get_event_bus().emit(event_type, data, source)


def subscribe(event_type: EventType, callback: Callable[[Event], None],
              filter_fn: Callable[[Event], bool] = None,
              once: bool = False) -> str:
    """Suscribe al bus global."""
    return get_event_bus().subscribe(event_type, callback, filter_fn, once)


# =============================================================================
# EVENT HELPERS
# =============================================================================

def create_agent_event(event_type: EventType, agent_name: str,
                       **kwargs) -> Event:
    """Crea un evento de agente."""
    return Event(
        type=event_type,
        data={"agent": agent_name, **kwargs},
        source=f"agent.{agent_name}"
    )


def create_workflow_event(event_type: EventType, workflow_name: str,
                          step: str = None, **kwargs) -> Event:
    """Crea un evento de workflow."""
    data = {"workflow": workflow_name, **kwargs}
    if step:
        data["step"] = step
    return Event(
        type=event_type,
        data=data,
        source=f"workflow.{workflow_name}"
    )


def create_mcp_event(event_type: EventType, server_name: str,
                     **kwargs) -> Event:
    """Crea un evento de MCP."""
    return Event(
        type=event_type,
        data={"server": server_name, **kwargs},
        source=f"mcp.{server_name}"
    )


# =============================================================================
# CLI
# =============================================================================

def main():
    """Demo del Event Bus."""
    import argparse

    parser = argparse.ArgumentParser(description="NXT Event Bus Demo")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    args = parser.parse_args()

    if args.demo:
        bus = EventBus()

        # Suscribir a eventos
        def on_task_started(event):
            print(f"[HANDLER] Task started: {event.data.get('task')}")

        def on_agent_activated(event):
            print(f"[HANDLER] Agent activated: {event.data.get('agent')}")

        bus.subscribe(EventType.TASK_STARTED, on_task_started)
        bus.subscribe(EventType.AGENT_ACTIVATED, on_agent_activated)

        # Emitir eventos
        print("\n=== Event Bus Demo ===\n")

        bus.emit(EventType.SYSTEM_INIT, {"version": "3.8.0"})
        bus.emit(EventType.TASK_STARTED, {"task": "Implement authentication"})
        bus.emit(EventType.AGENT_ACTIVATED, {"agent": "nxt-architect"})
        bus.emit(EventType.WORKFLOW_STEP_COMPLETED, {"step": "design", "duration": "5m"})

        # Mostrar historial
        print("\n=== Event History ===\n")
        for event in bus.get_history():
            print(f"  {event.type.value}: {event.data}")

        print(f"\nTotal subscriptions: {bus.get_subscription_count()}")
        print(f"Total events in history: {len(bus.get_history())}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
