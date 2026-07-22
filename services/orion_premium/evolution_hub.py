from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class EvolutionTarget:
    target_type: str
    target_id: str
    capability: str


@dataclass
class EvolutionProposal:
    proposal_id: str
    title: str
    objective: str
    evidence: List[Dict[str, Any]]
    targets: List[EvolutionTarget]
    proposed_changes: List[Dict[str, Any]]
    risk: str
    rollback: str
    confidence: float
    created_by: str = "orion"
    status: str = "proposal_only"
    human_approval_required: bool = True
    created_at: int = field(default_factory=lambda: int(time.time()))
    integrity_hash: str = ""

    def seal(self) -> "EvolutionProposal":
        body = self.to_dict(include_hash=False)
        self.integrity_hash = hashlib.sha256(
            json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return self

    def to_dict(self, *, include_hash: bool = True) -> Dict[str, Any]:
        payload = asdict(self)
        if not include_hash:
            payload.pop("integrity_hash", None)
        return payload


def build_evolution_proposal(
    *,
    title: str,
    objective: str,
    evidence: Iterable[Dict[str, Any]],
    targets: Iterable[EvolutionTarget],
    proposed_changes: Iterable[Dict[str, Any]],
    risk: str,
    rollback: str,
    confidence: float,
    created_by: str = "orion",
) -> EvolutionProposal:
    evidence_list = [dict(item) for item in evidence if isinstance(item, dict)]
    target_list = list(targets)
    change_list = [dict(item) for item in proposed_changes if isinstance(item, dict)]
    if not evidence_list:
        raise ValueError("evidence_required")
    if not target_list:
        raise ValueError("target_required")
    if not change_list:
        raise ValueError("proposed_change_required")
    if not str(rollback or "").strip():
        raise ValueError("rollback_required")
    confidence_value = max(0.0, min(float(confidence), 1.0))
    proposal = EvolutionProposal(
        proposal_id=uuid.uuid4().hex,
        title=str(title or "").strip(),
        objective=str(objective or "").strip(),
        evidence=evidence_list,
        targets=target_list,
        proposed_changes=change_list,
        risk=str(risk or "unknown").strip(),
        rollback=str(rollback).strip(),
        confidence=confidence_value,
        created_by=str(created_by or "orion").strip(),
    )
    return proposal.seal()


def can_execute(proposal: EvolutionProposal, *, human_approved: bool) -> bool:
    return bool(
        proposal.status == "approved"
        and human_approved
        and proposal.integrity_hash
        and proposal.rollback
        and proposal.evidence
    )


def build_agent_dispatch_plan(proposal: EvolutionProposal) -> Dict[str, Any]:
    return {
        "proposal_id": proposal.proposal_id,
        "mode": "proposal_only",
        "speaker": "orion",
        "targets": [
            {
                "target_type": item.target_type,
                "target_id": item.target_id,
                "capability": item.capability,
                "action": "review_and_return_diff",
            }
            for item in proposal.targets
        ],
        "human_approval_required": True,
        "execution_allowed": False,
    }
