"""
ORKIO Platform Services — OEP-010.2 Metrics.

Dependency-free in-memory metrics primitives for smoke/regression and local
operational accounting. This is not a replacement for Prometheus/OpenTelemetry;
it is a safe foundation that can later be bridged to enterprise telemetry.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import perf_counter
from typing import Dict, Iterable, Mapping, Optional


class MetricKind(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    TIMER = "timer"


@dataclass
class MetricSnapshot:
    name: str
    kind: MetricKind
    value: float
    count: int = 0
    tags: Mapping[str, str] = field(default_factory=dict)


class MetricsRegistry:
    """Small deterministic metrics registry."""

    def __init__(self) -> None:
        self._values: Dict[str, MetricSnapshot] = {}

    @staticmethod
    def _key(name: str, tags: Optional[Mapping[str, str]] = None) -> str:
        if not name or not name.strip():
            raise ValueError("metric name is required")
        safe_tags = tags or {}
        encoded_tags = ",".join(f"{k}={safe_tags[k]}" for k in sorted(safe_tags))
        return f"{name}|{encoded_tags}"

    def increment(self, name: str, amount: float = 1.0, tags: Optional[Mapping[str, str]] = None) -> MetricSnapshot:
        key = self._key(name, tags)
        current = self._values.get(key)
        if current is None:
            current = MetricSnapshot(name=name, kind=MetricKind.COUNTER, value=0.0, count=0, tags=dict(tags or {}))
        if current.kind != MetricKind.COUNTER:
            raise ValueError(f"metric {name} is not a counter")
        current.value += amount
        current.count += 1
        self._values[key] = current
        return current

    def gauge(self, name: str, value: float, tags: Optional[Mapping[str, str]] = None) -> MetricSnapshot:
        key = self._key(name, tags)
        snapshot = MetricSnapshot(name=name, kind=MetricKind.GAUGE, value=float(value), count=1, tags=dict(tags or {}))
        self._values[key] = snapshot
        return snapshot

    def observe_ms(self, name: str, elapsed_ms: float, tags: Optional[Mapping[str, str]] = None) -> MetricSnapshot:
        key = self._key(name, tags)
        current = self._values.get(key)
        if current is None:
            current = MetricSnapshot(name=name, kind=MetricKind.TIMER, value=0.0, count=0, tags=dict(tags or {}))
        if current.kind != MetricKind.TIMER:
            raise ValueError(f"metric {name} is not a timer")
        current.value += float(elapsed_ms)
        current.count += 1
        self._values[key] = current
        return current

    def snapshot(self) -> Dict[str, object]:
        metrics = []
        for item in sorted(self._values.values(), key=lambda metric: (metric.name, sorted(metric.tags.items()))):
            payload = {
                "name": item.name,
                "kind": item.kind.value,
                "value": item.value,
                "count": item.count,
                "tags": dict(item.tags),
            }
            if item.kind == MetricKind.TIMER and item.count:
                payload["avg_ms"] = item.value / item.count
            metrics.append(payload)
        return {"total": len(metrics), "metrics": metrics}


class Timer:
    def __init__(self, registry: MetricsRegistry, name: str, tags: Optional[Mapping[str, str]] = None) -> None:
        self.registry = registry
        self.name = name
        self.tags = tags
        self._started = 0.0

    def __enter__(self) -> "Timer":
        self._started = perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        elapsed_ms = (perf_counter() - self._started) * 1000
        self.registry.observe_ms(self.name, elapsed_ms, self.tags)


_global_registry = MetricsRegistry()


def get_metrics_registry() -> MetricsRegistry:
    return _global_registry


def metrics_snapshot() -> Dict[str, object]:
    return _global_registry.snapshot()
