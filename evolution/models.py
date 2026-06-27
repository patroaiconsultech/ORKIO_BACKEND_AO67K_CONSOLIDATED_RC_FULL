from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

OEP_001_MODEL_VERSION = "OEP_001_EVOLUTION_DOMAIN_MODELS_V1"

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"

@dataclass
class Evidence:
    source: str
    payload: Dict[str, Any]
    type: str = "other"
    confidence: float = 0.5
    evidence_id: str = field(default_factory=lambda: new_id("evd"))
    created_at: str = field(default_factory=utc_now_iso)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Incident:
    title: str
    description: str
    severity: str = "medium"
    status: str = "open"
    incident_id: str = field(default_factory=lambda: new_id("inc"))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    closed_at: Optional[str] = None
    evidence_ids: List[str] = field(default_factory=list)
    proposal_ids: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    owner_agent: str = "orion"

    def touch(self) -> None:
        self.updated_at = utc_now_iso()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class Proposal:
    incident_id: str
    summary: str
    files: List[str]
    diff_preview: str = ""
    risk: str = "medium"
    confidence: float = 0.5
    rollback_plan: str = ""
    tests: List[str] = field(default_factory=list)
    proposal_id: str = field(default_factory=lambda: new_id("prop"))
    status: str = "ready_for_review"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = utc_now_iso()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GovernanceDecision:
    allowed: bool
    reason: str
    proposal_id: str
    required_actions: List[str] = field(default_factory=list)
    checked_at: str = field(default_factory=utc_now_iso)
    policy_version: str = "OEP_001_GOVERNANCE_POLICY_V1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ExecutionRecord:
    proposal_id: str
    executed: bool = False
    execution_id: str = field(default_factory=lambda: new_id("exec"))
    approved_by: Optional[str] = None
    executed_at: Optional[str] = None
    result: str = "not_executed"
    smoke_result: str = "not_run"
    rollback_executed: bool = False
    write_executed: bool = False
    logs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class LearningRecord:
    proposal_id: str
    success: bool
    lessons: List[str]
    regression: bool = False
    confidence_delta: float = 0.0
    learning_id: str = field(default_factory=lambda: new_id("learn"))
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
