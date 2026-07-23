from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any

@dataclass(frozen=True)
class EvidenceArtifact:
    source_type: str
    source_ref: str
    fact: str
    confidence: float
    raw_hash: str | None = None
    collection_method: str = "direct_observation"

@dataclass(frozen=True)
class DiagnosisArtifact:
    primary_root_cause: str
    evidence_ids: tuple[str, ...]
    confidence: float
    affected_domains: tuple[str, ...] = ()
    affected_files: tuple[str, ...] = ()
    secondary_causes: tuple[str, ...] = ()
    false_positives: tuple[str, ...] = ()
    hypotheses: tuple[dict[str, Any], ...] = ()

@dataclass(frozen=True)
class ProposalArtifact:
    objective: str
    diagnosis_id: str
    evidence_ids: tuple[str, ...]
    affected_files: tuple[str, ...]
    diff_preview: str
    risk: dict[str, Any]
    rollback: dict[str, Any]
    tests: tuple[str, ...]
    proposal_only: bool = True
    requires_human_approval: bool = True
    status: str = "proposal_only"

@dataclass(frozen=True)
class GovernanceArtifact:
    proposal_id: str
    decision: str
    reasons: tuple[str, ...]
    policy_version: str
    approved_by: str | None = None
    target_environment: str = "sandbox"
    constraints: tuple[str, ...] = ("no_production",)

@dataclass(frozen=True)
class AgentTaskArtifact:
    requested_by: str
    assigned_agent: str
    specialty: str
    objective: str
    input_artifact_ids: tuple[str, ...]
    status: str = "created"
    output_artifact_id: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    error: str | None = None

@dataclass(frozen=True)
class AgentResultArtifact:
    task_id: str
    agent_id: str
    specialty: str
    summary: str
    findings: tuple[dict[str, Any], ...]
    confidence: float
    cited_agent: str
    evidence_ids: tuple[str, ...] = ()

@dataclass(frozen=True)
class ExecutionArtifact:
    proposal_id: str
    governance_id: str
    workspace_id: str
    applied: bool
    files_changed: tuple[str, ...]
    commands_executed: tuple[tuple[str, ...], ...] = ()
    stdout_digest: str = ""
    stderr_digest: str = ""

@dataclass(frozen=True)
class ValidationArtifact:
    execution_id: str
    score: int
    status: str
    checks: tuple[dict[str, Any], ...]
    blocking_failures: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    regressions: tuple[str, ...] = ()

@dataclass(frozen=True)
class OutcomeArtifact:
    cycle_id: str
    proposal_id: str
    execution_id: str
    validation_id: str
    result: str
    success: bool
    regressions: tuple[str, ...] = ()
    rollback_required: bool = False
    human_review: str = ""
    lessons: tuple[str, ...] = ()

def payload_of(value: Any) -> dict[str, Any]:
    return asdict(value)
