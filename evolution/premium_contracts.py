from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


ORION_EVOLUTION_CONTRACT_VERSION = "ORION_EVOLUTION_R20_V1"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:16]}"


@dataclass(frozen=True)
class RiskAssessment:
    level: str
    score: int
    reasons: List[str] = field(default_factory=list)
    blast_radius: str = "local"
    touches_database: bool = False
    touches_auth: bool = False
    touches_runtime_boot: bool = False
    touches_deploy: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RollbackPlan:
    strategy: str
    commands: List[str] = field(default_factory=list)
    data_restore_required: bool = False
    migration_downgrade_required: bool = False
    verification_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SimulationReport:
    passed: bool
    checks: List[Dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    generated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EvolutionPlan:
    objective: str
    evidence: List[Dict[str, Any]]
    root_cause: str
    files: List[str]
    diff_preview: str
    risk: RiskAssessment
    rollback: RollbackPlan
    tests: List[str]
    proposal_id: str = field(default_factory=lambda: new_id("orion_prop"))
    status: str = "proposal_only"
    proposal_only: bool = True
    requires_human_approval: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    simulation: Optional[SimulationReport] = None
    execution_mode: str = "none"
    target_environment: str = "branch"
    branch_name: Optional[str] = None
    write_executed: bool = False
    created_at: str = field(default_factory=utc_now_iso)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def approve(self, approver: str) -> None:
        self.approved_by = approver
        self.approved_at = utc_now_iso()
        self.status = "approved_for_branch"

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        return payload
