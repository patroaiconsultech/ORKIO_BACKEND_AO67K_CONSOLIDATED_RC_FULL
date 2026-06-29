from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _proposal_id() -> str:
    return f"proposal_{uuid4().hex[:16]}"

@dataclass(frozen=True)
class ProposalEvidence:
    source_id: str
    title: str
    excerpt: str
    score: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class ProposalRisk:
    level: str
    description: str
    mitigation: str = ""
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class Proposal:
    title: str
    summary: str
    recommendation: str
    evidence: list[ProposalEvidence]
    risks: list[ProposalRisk] = field(default_factory=list)
    confidence: float = 0.0
    source_documents: list[str] = field(default_factory=list)
    proposal_id: str = field(default_factory=_proposal_id)
    created_at: str = field(default_factory=_now)
    proposal_only: bool = True
    requires_human_approval: bool = True
    write_executed: bool = False
    status: str = "draft"
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate_governance(self) -> None:
        if self.proposal_only is not True:
            raise ValueError("proposal_only must be True")
        if self.requires_human_approval is not True:
            raise ValueError("requires_human_approval must be True")
        if self.write_executed is not False:
            raise ValueError("write_executed must be False")
        if not (0.0 <= float(self.confidence) <= 1.0):
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not self.evidence:
            raise ValueError("proposal requires at least one evidence item")

    def to_dict(self) -> dict[str, Any]:
        self.validate_governance()
        return {
            "proposal_id": self.proposal_id, "title": self.title, "summary": self.summary,
            "recommendation": self.recommendation,
            "evidence": [item.to_dict() for item in self.evidence],
            "risks": [risk.to_dict() for risk in self.risks],
            "confidence": self.confidence, "source_documents": list(self.source_documents),
            "created_at": self.created_at, "proposal_only": self.proposal_only,
            "requires_human_approval": self.requires_human_approval,
            "write_executed": self.write_executed, "status": self.status,
            "metadata": dict(self.metadata),
        }
