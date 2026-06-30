"""
ORKIO Platform Services — OEP-010.4 Security Audit Foundation.

Read-only security audit primitives. This module does not mutate configuration,
does not call external services, and is suitable for proposal-only governance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Mapping, Optional


class SecuritySeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class SecurityAuditFinding:
    code: str
    title: str
    severity: SecuritySeverity
    message: str
    remediation: str = ""
    metadata: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "code": self.code,
            "title": self.title,
            "severity": self.severity.value,
            "message": self.message,
            "remediation": self.remediation,
            "metadata": dict(self.metadata),
        }


class SecurityAuditService:
    """Read-only scanner for common platform readiness risks."""

    REQUIRED_GOVERNANCE_FLAGS = {
        "proposal_only": True,
        "write_executed": False,
        "human_approval_required": True,
    }

    def audit_governance_flags(self, flags: Mapping[str, object]) -> List[SecurityAuditFinding]:
        findings: List[SecurityAuditFinding] = []
        for key, expected in self.REQUIRED_GOVERNANCE_FLAGS.items():
            actual = flags.get(key)
            if actual != expected:
                findings.append(
                    SecurityAuditFinding(
                        code="GOVERNANCE_FLAG_MISMATCH",
                        title=f"Governance flag {key} is not preserved",
                        severity=SecuritySeverity.HIGH,
                        message=f"Expected {key}={expected!r}, got {actual!r}.",
                        remediation="Restore the governed evolution safety flag before release.",
                        metadata={"flag": key, "expected": expected, "actual": actual},
                    )
                )
        return findings

    def audit_required_env_names(self, env: Mapping[str, str], required_names: Iterable[str]) -> List[SecurityAuditFinding]:
        findings: List[SecurityAuditFinding] = []
        for name in required_names:
            if not env.get(name):
                findings.append(
                    SecurityAuditFinding(
                        code="REQUIRED_ENV_MISSING",
                        title=f"Required environment variable missing: {name}",
                        severity=SecuritySeverity.MEDIUM,
                        message=f"{name} is required for production readiness.",
                        remediation="Set the variable in the deployment environment.",
                        metadata={"env_name": name},
                    )
                )
        return findings

    def audit_secret_exposure(self, payload: Mapping[str, object]) -> List[SecurityAuditFinding]:
        findings: List[SecurityAuditFinding] = []
        sensitive_markers = ("secret", "token", "password", "api_key", "apikey", "private_key")
        for key, value in payload.items():
            normalized = key.lower()
            if any(marker in normalized for marker in sensitive_markers) and value:
                findings.append(
                    SecurityAuditFinding(
                        code="POTENTIAL_SECRET_EXPOSURE",
                        title="Potential secret exposed in payload",
                        severity=SecuritySeverity.CRITICAL,
                        message=f"Sensitive-looking field {key!r} should not be exposed.",
                        remediation="Redact or remove this field from logs, metrics, events, and public API responses.",
                        metadata={"field": key},
                    )
                )
        return findings

    def summarize(self, findings: Iterable[SecurityAuditFinding]) -> Dict[str, object]:
        finding_list = list(findings)
        severity_rank = {
            SecuritySeverity.INFO: 0,
            SecuritySeverity.LOW: 1,
            SecuritySeverity.MEDIUM: 2,
            SecuritySeverity.HIGH: 3,
            SecuritySeverity.CRITICAL: 4,
        }
        max_severity = SecuritySeverity.INFO
        for finding in finding_list:
            if severity_rank[finding.severity] > severity_rank[max_severity]:
                max_severity = finding.severity
        return {
            "total": len(finding_list),
            "max_severity": max_severity.value,
            "release_blocked": any(
                finding.severity in {SecuritySeverity.HIGH, SecuritySeverity.CRITICAL}
                for finding in finding_list
            ),
            "findings": [finding.to_dict() for finding in finding_list],
        }


def run_default_security_audit(flags: Optional[Mapping[str, object]] = None) -> Dict[str, object]:
    service = SecurityAuditService()
    governed_flags = flags or {
        "proposal_only": True,
        "write_executed": False,
        "human_approval_required": True,
    }
    findings = service.audit_governance_flags(governed_flags)
    return service.summarize(findings)
