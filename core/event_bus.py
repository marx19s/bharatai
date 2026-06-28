"""
=================================================
BharatAI
Event Bus (Decoupled event-driven orchestration)
=================================================
"""

import time
import logging
import threading
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field

from config.settings import LOG_FILE, LOG_LEVEL

logger = logging.getLogger("bharatai.core.event_bus")
if not logger.handlers:
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    try:
        fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
    except Exception:
        pass


@dataclass
class Event:
    """Represents a standard event dispatched through the event bus."""
    type: str
    sender: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class EventBus:
    """Decoupled, thread-safe Event Bus allowing agents to coordinate asynchronously."""

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self._lock = threading.Lock()
        logger.info("EventBus initialized.")

    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Register a callback for a specific event type (or '*' for all events)."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                logger.info(f"Subscribed callback to event type: '{event_type}'")

    def unsubscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        """Remove a subscriber callback."""
        with self._lock:
            if event_type in self._subscribers and callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                logger.info(f"Unsubscribed callback from event type: '{event_type}'")

    def publish(self, event_type: str, sender: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """Publish an event to all subscribed callbacks."""
        event = Event(type=event_type, sender=sender, payload=payload or {})
        logger.info(f"Event published: Type='{event_type}', Sender='{sender}'")

        # Snapshot callbacks under lock to prevent lock contention during callback runs
        callbacks = []
        with self._lock:
            if event_type in self._subscribers:
                callbacks.extend(self._subscribers[event_type])
            if "*" in self._subscribers:
                callbacks.extend(self._subscribers["*"])

        for callback in callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error executing callback subscription for event type '{event_type}': {e}")


# Export a global event bus instance
event_bus = EventBus()
