from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List
import time
import uuid


@dataclass(frozen=True)
class CognitiveEvent:
    name: str
    payload: Dict[str, Any]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: float = field(default_factory=time.time)


class InMemoryEventBus:
    """Minimal synchronous event bus for Shadow Mode and tests."""

    def __init__(self) -> None:
        self._events: List[CognitiveEvent] = []
        self._subscribers: Dict[str, List[Callable[[CognitiveEvent], None]]] = {}

    def publish(self, name: str, payload: Dict[str, Any]) -> CognitiveEvent:
        event = CognitiveEvent(name=name, payload=payload)
        self._events.append(event)
        for callback in self._subscribers.get(name, []):
            callback(event)
        for callback in self._subscribers.get("*", []):
            callback(event)
        return event

    def subscribe(self, name: str, callback: Callable[[CognitiveEvent], None]) -> None:
        self._subscribers.setdefault(name, []).append(callback)

    def events(self) -> List[CognitiveEvent]:
        return list(self._events)
