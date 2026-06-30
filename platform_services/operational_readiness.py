"""
ORKIO Platform Services — OEP-010.5 Operational Readiness Report.

Combines health, metrics, observability, and security audit into an API-safe
GO/NO-GO operational report.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Mapping, Optional

from platform_services.health_checks import HealthStatus, run_default_health_checks
from platform_services.metrics import metrics_snapshot
from platform_services.observability_events import list_observability_events
from platform_services.security_audit import run_default_security_audit


@dataclass(frozen=True)
class OperationalReadinessReport:
    release_name: str
    go: bool
    status: str
    generated_at: str
    health: Mapping[str, object] = field(default_factory=dict)
    metrics: Mapping[str, object] = field(default_factory=dict)
    observability: Mapping[str, object] = field(default_factory=dict)
    security: Mapping[str, object] = field(default_factory=dict)
    notes: str = ""

    def to_dict(self) -> Dict[str, object]:
        return {
            "release_name": self.release_name,
            "go": self.go,
            "status": self.status,
            "generated_at": self.generated_at,
            "health": dict(self.health),
            "metrics": dict(self.metrics),
            "observability": dict(self.observability),
            "security": dict(self.security),
            "notes": self.notes,
        }


def generate_operational_readiness_report(
    release_name: str = "v0.10.0-beta",
    governance_flags: Optional[Mapping[str, object]] = None,
) -> Dict[str, object]:
    health = run_default_health_checks()
    metrics = metrics_snapshot()
    events = list_observability_events(limit=50)
    security = run_default_security_audit(governance_flags)

    health_ok = health.get("overall_status") == HealthStatus.HEALTHY.value
    security_ok = not bool(security.get("release_blocked"))

    go = health_ok and security_ok
    status = "GO" if go else "NO-GO"

    report = OperationalReadinessReport(
        release_name=release_name,
        go=go,
        status=status,
        generated_at=datetime.now(timezone.utc).isoformat(),
        health=health,
        metrics=metrics,
        observability={"total_recent_events": len(events), "events": events},
        security=security,
        notes="Operational readiness foundation is additive and read-only.",
    )
    return report.to_dict()
