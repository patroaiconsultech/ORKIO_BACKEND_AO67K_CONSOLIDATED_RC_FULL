"""
ORKIO Platform Services — OEP-010.1 Health Checks.

Additive, dependency-free foundation for enterprise operational health checks.
Preserves baseline behavior and does not execute external writes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from time import time
from typing import Callable, Dict, Iterable, List, Mapping, Optional


class HealthStatus(str, Enum):
    """Stable health states for operational checks."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class HealthCheckResult:
    """Result of a single health check."""

    name: str
    status: HealthStatus
    message: str = ""
    latency_ms: float = 0.0
    details: Mapping[str, object] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status == HealthStatus.HEALTHY


HealthCheckCallable = Callable[[], HealthCheckResult]


class HealthCheckRegistry:
    """Small in-memory registry for health checks.

    The registry is intentionally simple to avoid coupling operational readiness
    to web framework, database, or external provider availability.
    """

    def __init__(self) -> None:
        self._checks: Dict[str, HealthCheckCallable] = {}

    def register(self, name: str, check: HealthCheckCallable) -> None:
        if not name or not name.strip():
            raise ValueError("health check name is required")
        if not callable(check):
            raise TypeError("health check must be callable")
        self._checks[name] = check

    def unregister(self, name: str) -> None:
        self._checks.pop(name, None)

    def names(self) -> List[str]:
        return sorted(self._checks.keys())

    def run_one(self, name: str) -> HealthCheckResult:
        if name not in self._checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message="health check not registered",
            )

        started = time()
        try:
            result = self._checks[name]()
            latency_ms = (time() - started) * 1000
            if result.latency_ms:
                return result
            return HealthCheckResult(
                name=result.name or name,
                status=result.status,
                message=result.message,
                latency_ms=latency_ms,
                details=result.details,
            )
        except Exception as exc:  # defensive boundary for operational probes
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"{type(exc).__name__}: {exc}",
                latency_ms=(time() - started) * 1000,
            )

    def run_all(self, names: Optional[Iterable[str]] = None) -> List[HealthCheckResult]:
        target_names = list(names) if names is not None else self.names()
        return [self.run_one(name) for name in target_names]


def summarize_health(results: Iterable[HealthCheckResult]) -> Dict[str, object]:
    """Return an API-safe summary for a group of health results."""

    result_list = list(results)
    if not result_list:
        overall = HealthStatus.UNKNOWN
    elif any(item.status == HealthStatus.UNHEALTHY for item in result_list):
        overall = HealthStatus.UNHEALTHY
    elif any(item.status == HealthStatus.DEGRADED for item in result_list):
        overall = HealthStatus.DEGRADED
    elif all(item.status == HealthStatus.HEALTHY for item in result_list):
        overall = HealthStatus.HEALTHY
    else:
        overall = HealthStatus.UNKNOWN

    return {
        "overall_status": overall.value,
        "total": len(result_list),
        "healthy": sum(1 for item in result_list if item.status == HealthStatus.HEALTHY),
        "degraded": sum(1 for item in result_list if item.status == HealthStatus.DEGRADED),
        "unhealthy": sum(1 for item in result_list if item.status == HealthStatus.UNHEALTHY),
        "unknown": sum(1 for item in result_list if item.status == HealthStatus.UNKNOWN),
        "checks": [
            {
                "name": item.name,
                "status": item.status.value,
                "message": item.message,
                "latency_ms": round(item.latency_ms, 3),
                "details": dict(item.details),
            }
            for item in result_list
        ],
    }


def platform_baseline_check() -> HealthCheckResult:
    return HealthCheckResult(
        name="platform_baseline",
        status=HealthStatus.HEALTHY,
        message="platform services import boundary is healthy",
    )


def create_default_health_registry() -> HealthCheckRegistry:
    registry = HealthCheckRegistry()
    registry.register("platform_baseline", platform_baseline_check)
    return registry


def run_default_health_checks() -> Dict[str, object]:
    registry = create_default_health_registry()
    return summarize_health(registry.run_all())
