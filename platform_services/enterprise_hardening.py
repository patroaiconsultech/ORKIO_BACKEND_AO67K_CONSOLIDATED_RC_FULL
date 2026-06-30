"""
ORKIO Platform Services — OEP-010.6 Enterprise Operations Hardening.

Additive hardening layer for v0.10.1. It normalizes operational status,
redacts sensitive fields from API-safe reports, evaluates release gates, and
generates deterministic operational action items.

No external dependencies. No network calls. No writes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Mapping, Optional, Sequence


class OperationalStatus(str, Enum):
    """Normalized operational status used by readiness gates."""

    GO = "GO"
    WARN = "WARN"
    NO_GO = "NO-GO"
    UNKNOWN = "UNKNOWN"


class HardeningSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class HardeningFinding:
    """A deterministic finding produced by the hardening layer."""

    code: str
    title: str
    severity: HardeningSeverity
    message: str
    action: str = ""
    metadata: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "code": self.code,
            "title": self.title,
            "severity": self.severity.value,
            "message": self.message,
            "action": self.action,
            "metadata": dict(self.metadata),
        }


SENSITIVE_MARKERS = (
    "secret",
    "token",
    "password",
    "api_key",
    "apikey",
    "authorization",
    "private_key",
)


def is_sensitive_key(key: object) -> bool:
    normalized = str(key).lower()
    return any(marker in normalized for marker in SENSITIVE_MARKERS)


def redact_sensitive_payload(payload: object, redaction: str = "***REDACTED***") -> object:
    """Return an API-safe copy of nested dictionaries/lists/tuples.

    This function is intentionally conservative: any key that looks sensitive
    has its value redacted, regardless of nesting depth.
    """

    if isinstance(payload, Mapping):
        safe: Dict[object, object] = {}
        for key, value in payload.items():
            if is_sensitive_key(key):
                safe[key] = redaction
            else:
                safe[key] = redact_sensitive_payload(value, redaction=redaction)
        return safe
    if isinstance(payload, list):
        return [redact_sensitive_payload(item, redaction=redaction) for item in payload]
    if isinstance(payload, tuple):
        return tuple(redact_sensitive_payload(item, redaction=redaction) for item in payload)
    return payload


def normalize_operational_status(
    *,
    health_status: Optional[str] = None,
    release_blocked: bool = False,
    critical_findings: int = 0,
    degraded_allowed: bool = True,
) -> OperationalStatus:
    """Normalize health/security signals into a single release status."""

    normalized_health = (health_status or "unknown").lower()

    if release_blocked or critical_findings > 0:
        return OperationalStatus.NO_GO
    if normalized_health == "unhealthy":
        return OperationalStatus.NO_GO
    if normalized_health == "degraded":
        return OperationalStatus.WARN if degraded_allowed else OperationalStatus.NO_GO
    if normalized_health == "healthy":
        return OperationalStatus.GO
    return OperationalStatus.UNKNOWN


@dataclass(frozen=True)
class ReleaseGatePolicy:
    """Deterministic policy for GO/NO-GO evaluation."""

    allow_degraded_health: bool = False
    max_recent_error_events: int = 0
    max_high_findings: int = 0
    max_critical_findings: int = 0

    def evaluate(self, report: Mapping[str, object]) -> Dict[str, object]:
        findings: List[HardeningFinding] = []

        health = _mapping(report.get("health"))
        security = _mapping(report.get("security"))
        observability = _mapping(report.get("observability"))

        health_status = str(health.get("overall_status", "unknown")).lower()
        if health_status == "unhealthy":
            findings.append(
                HardeningFinding(
                    code="HEALTH_UNHEALTHY",
                    title="Operational health is unhealthy",
                    severity=HardeningSeverity.CRITICAL,
                    message="At least one health check is unhealthy.",
                    action="Fix failing health checks before promoting this release.",
                )
            )
        elif health_status == "degraded" and not self.allow_degraded_health:
            findings.append(
                HardeningFinding(
                    code="HEALTH_DEGRADED_BLOCKED",
                    title="Operational health is degraded",
                    severity=HardeningSeverity.HIGH,
                    message="Degraded health is not allowed by the current release policy.",
                    action="Resolve degraded checks or explicitly change the release policy.",
                )
            )
        elif health_status not in {"healthy", "degraded"}:
            findings.append(
                HardeningFinding(
                    code="HEALTH_UNKNOWN",
                    title="Operational health is unknown",
                    severity=HardeningSeverity.HIGH,
                    message="The readiness report did not provide a trusted health status.",
                    action="Ensure health checks are registered and included in readiness output.",
                    metadata={"health_status": health_status},
                )
            )

        security_blocked = bool(security.get("release_blocked", False))
        severity_counts = count_security_severities(security.get("findings", []))
        if security_blocked:
            findings.append(
                HardeningFinding(
                    code="SECURITY_RELEASE_BLOCKED",
                    title="Security audit blocks release",
                    severity=HardeningSeverity.CRITICAL,
                    message="Security audit reported release_blocked=true.",
                    action="Resolve high/critical security findings before release.",
                )
            )

        if severity_counts.get("high", 0) > self.max_high_findings:
            findings.append(
                HardeningFinding(
                    code="SECURITY_HIGH_FINDINGS",
                    title="Too many high security findings",
                    severity=HardeningSeverity.HIGH,
                    message="High severity finding count exceeds policy.",
                    action="Reduce high severity findings before release.",
                    metadata={"actual": severity_counts.get("high", 0), "allowed": self.max_high_findings},
                )
            )

        if severity_counts.get("critical", 0) > self.max_critical_findings:
            findings.append(
                HardeningFinding(
                    code="SECURITY_CRITICAL_FINDINGS",
                    title="Too many critical security findings",
                    severity=HardeningSeverity.CRITICAL,
                    message="Critical finding count exceeds policy.",
                    action="Resolve all critical findings before release.",
                    metadata={"actual": severity_counts.get("critical", 0), "allowed": self.max_critical_findings},
                )
            )

        recent_errors = count_recent_error_events(observability.get("events", []))
        if recent_errors > self.max_recent_error_events:
            findings.append(
                HardeningFinding(
                    code="OBSERVABILITY_ERROR_BUDGET_EXCEEDED",
                    title="Recent error events exceed policy",
                    severity=HardeningSeverity.HIGH,
                    message="Recent operational error event count exceeds policy.",
                    action="Inspect recent events and resolve active incidents before release.",
                    metadata={"actual": recent_errors, "allowed": self.max_recent_error_events},
                )
            )

        status = decide_status(findings)
        return {
            "status": status.value,
            "go": status == OperationalStatus.GO,
            "finding_count": len(findings),
            "findings": [finding.to_dict() for finding in findings],
            "policy": {
                "allow_degraded_health": self.allow_degraded_health,
                "max_recent_error_events": self.max_recent_error_events,
                "max_high_findings": self.max_high_findings,
                "max_critical_findings": self.max_critical_findings,
            },
            "sanitized_report": redact_sensitive_payload(report),
        }


def _mapping(value: object) -> Mapping[str, object]:
    return value if isinstance(value, Mapping) else {}


def count_security_severities(findings: object) -> Dict[str, int]:
    counts = {"info": 0, "low": 0, "medium": 0, "high": 0, "critical": 0}
    if not isinstance(findings, Iterable) or isinstance(findings, (str, bytes, Mapping)):
        return counts
    for item in findings:
        if isinstance(item, Mapping):
            severity = str(item.get("severity", "info")).lower()
            if severity in counts:
                counts[severity] += 1
    return counts


def count_recent_error_events(events: object) -> int:
    if not isinstance(events, Iterable) or isinstance(events, (str, bytes, Mapping)):
        return 0
    total = 0
    for event in events:
        if isinstance(event, Mapping) and str(event.get("severity", "")).lower() in {"error", "critical", "fatal"}:
            total += 1
    return total


def decide_status(findings: Sequence[HardeningFinding]) -> OperationalStatus:
    if any(finding.severity == HardeningSeverity.CRITICAL for finding in findings):
        return OperationalStatus.NO_GO
    if any(finding.severity == HardeningSeverity.HIGH for finding in findings):
        return OperationalStatus.NO_GO
    if findings:
        return OperationalStatus.WARN
    return OperationalStatus.GO


def generate_hardened_readiness_report(
    report: Mapping[str, object],
    policy: Optional[ReleaseGatePolicy] = None,
) -> Dict[str, object]:
    """Evaluate an existing readiness report through the hardening gate."""

    effective_policy = policy or ReleaseGatePolicy()
    gate = effective_policy.evaluate(report)
    return {
        "release_name": report.get("release_name", "unknown"),
        "status": gate["status"],
        "go": gate["go"],
        "hardening": gate,
    }
