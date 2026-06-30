"""
ORKIO Platform Services — OEP-010.3 Observability Events.

Structured, bounded, in-memory event stream for operational visibility.
No external side effects. Safe for tests and later API exposure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Mapping, Optional
from uuid import uuid4


@dataclass(frozen=True)
class ObservabilityEvent:
    event_type: str
    message: str
    severity: str = "info"
    source: str = "platform_services"
    event_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    correlation_id: Optional[str] = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "message": self.message,
            "severity": self.severity,
            "source": self.source,
            "created_at": self.created_at,
            "correlation_id": self.correlation_id,
            "metadata": dict(self.metadata),
        }


class ObservabilityEventBus:
    """Bounded in-memory event bus."""

    def __init__(self, max_events: int = 500) -> None:
        if max_events <= 0:
            raise ValueError("max_events must be positive")
        self.max_events = max_events
        self._events: List[ObservabilityEvent] = []

    def emit(
        self,
        event_type: str,
        message: str,
        *,
        severity: str = "info",
        source: str = "platform_services",
        correlation_id: Optional[str] = None,
        metadata: Optional[Mapping[str, object]] = None,
    ) -> ObservabilityEvent:
        if not event_type or not event_type.strip():
            raise ValueError("event_type is required")
        event = ObservabilityEvent(
            event_type=event_type,
            message=message,
            severity=severity,
            source=source,
            correlation_id=correlation_id,
            metadata=dict(metadata or {}),
        )
        self._events.append(event)
        if len(self._events) > self.max_events:
            self._events = self._events[-self.max_events :]
        return event

    def list_events(self, limit: Optional[int] = None, severity: Optional[str] = None) -> List[Dict[str, object]]:
        events = self._events
        if severity:
            events = [event for event in events if event.severity == severity]
        if limit is not None:
            events = events[-limit:]
        return [event.to_dict() for event in events]

    def clear(self) -> None:
        self._events.clear()


_global_bus = ObservabilityEventBus()


def get_observability_event_bus() -> ObservabilityEventBus:
    return _global_bus


def emit_observability_event(event_type: str, message: str, **kwargs) -> Dict[str, object]:
    return _global_bus.emit(event_type, message, **kwargs).to_dict()


def list_observability_events(limit: Optional[int] = None, severity: Optional[str] = None) -> List[Dict[str, object]]:
    return _global_bus.list_events(limit=limit, severity=severity)
