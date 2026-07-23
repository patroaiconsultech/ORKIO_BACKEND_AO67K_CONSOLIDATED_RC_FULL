from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


class ProposalStatus(str, Enum):
    DRAFT = "draft"
    PROPOSAL_ONLY = "proposal_only"
    SIMULATED = "simulated"
    APPROVAL_REQUIRED = "approval_required"
    APPROVED_FOR_BRANCH = "approved_for_branch"
    BRANCH_EXECUTION_READY = "branch_execution_ready"
    VALIDATION_READY = "validation_ready"
    REVIEW_READY = "review_ready"
    REJECTED = "rejected"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Evidence:
    source_type: str
    source_ref: str
    fact: str
    confidence: float
    evidence_id: str = field(default_factory=lambda: new_id("evidence"))
    collected_at: str = field(default_factory=utc_now)
    raw_hash: Optional[str] = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("evidence_confidence_out_of_range")


@dataclass(frozen=True)
class Hypothesis:
    statement: str
    supporting_evidence_ids: List[str]
    contradicting_evidence_ids: List[str] = field(default_factory=list)
    confidence: float = 0.0
    status: str = "open"
    hypothesis_id: str = field(default_factory=lambda: new_id("hypothesis"))


@dataclass(frozen=True)
class Diagnosis:
    primary_root_cause: str
    evidence_ids: List[str]
    confidence: float
    affected_domains: List[str] = field(default_factory=list)
    affected_files: List[str] = field(default_factory=list)
    secondary_causes: List[str] = field(default_factory=list)
    false_positives: List[str] = field(default_factory=list)
    diagnosis_id: str = field(default_factory=lambda: new_id("diagnosis"))


@dataclass
class EvolutionProposal:
    objective: str
    files: List[str]
    diff_preview: str
    tests: List[str]
    rollback: Dict[str, Any]
    risk: Dict[str, Any]
    evidence_ids: List[str] = field(default_factory=list)
    diagnosis_id: Optional[str] = None
    proposal_id: str = field(default_factory=lambda: new_id("proposal"))
    status: str = ProposalStatus.PROPOSAL_ONLY.value
    proposal_only: bool = True
    requires_human_approval: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    branch_name: Optional[str] = None
    created_at: str = field(default_factory=utc_now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def approve(self, approver: str) -> None:
        name = str(approver or "").strip()
        if not name:
            raise ValueError("named_human_approver_required")
        self.approved_by = name
        self.approved_at = utc_now()
        self.status = ProposalStatus.APPROVED_FOR_BRANCH.value


@dataclass(frozen=True)
class PatchArtifact:
    proposal_id: str
    unified_diff: str
    files_changed: List[str]
    before_hashes: Dict[str, str]
    expected_after_hashes: Dict[str, str]
    patch_id: str = field(default_factory=lambda: new_id("patch"))
    format: str = "unified_diff"
    generated_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class ExecutionReport:
    patch_id: str
    workspace_path: str
    applied: bool
    files_changed: List[str]
    stdout: str = ""
    stderr: str = ""
    commands_executed: List[List[str]] = field(default_factory=list)
    execution_id: str = field(default_factory=lambda: new_id("execution"))
    created_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class ValidationReport:
    patch_id: str
    score: int
    status: str
    checks: List[Dict[str, Any]]
    blocking_failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    regressions: List[str] = field(default_factory=list)
    validation_id: str = field(default_factory=lambda: new_id("validation"))
    created_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class GovernanceDecision:
    allowed: bool
    action: str
    reasons: List[str]
    requires_human_approval: bool = True
    decision_id: str = field(default_factory=lambda: new_id("decision"))
    decided_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class OrionEvent:
    event_type: str
    cycle_id: str
    correlation_id: str
    producer: str
    payload: Dict[str, Any]
    event_id: str = field(default_factory=lambda: new_id("event"))
    occurred_at: str = field(default_factory=utc_now)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
