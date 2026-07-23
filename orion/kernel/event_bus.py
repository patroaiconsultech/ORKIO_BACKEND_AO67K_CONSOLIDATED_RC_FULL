from __future__ import annotations

from collections import defaultdict
from typing import Callable, DefaultDict, List

from orion.contracts.models import OrionEvent


class EventBus:
    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, List[Callable[[OrionEvent], None]]] = defaultdict(list)
        self._audit: list[OrionEvent] = []

    def subscribe(self, event_type: str, handler: Callable[[OrionEvent], None]) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event: OrionEvent) -> None:
        self._audit.append(event)
        for handler in tuple(self._subscribers.get(event.event_type, ())):
            handler(event)

    def audit_trail(self, cycle_id: str | None = None) -> list[OrionEvent]:
        if cycle_id is None:
            return list(self._audit)
        return [event for event in self._audit if event.cycle_id == cycle_id]
