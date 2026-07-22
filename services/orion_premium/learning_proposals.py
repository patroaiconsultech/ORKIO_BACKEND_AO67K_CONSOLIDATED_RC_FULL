"""Governed learning proposals; persistence remains external and approval-gated."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Sequence

from .policies import MIN_LEARNING_CONFIDENCE, REQUIRE_HUMAN_APPROVAL


@dataclass(frozen=True)
class LearningProposal:
    key: str
    previous_value: Any
    proposed_value: Any
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.0
    risk: str = "low"
    rollback_value: Any = None
    approved_by: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["evidence_refs"] = list(self.evidence_refs)
        return payload


def create_learning_proposal(
    *,
    key: str,
    previous_value: Any,
    proposed_value: Any,
    evidence_refs: Sequence[str],
    confidence: float,
    risk: str = "low",
    approved_by: str | None = None,
) -> LearningProposal:
    return LearningProposal(
        key=key.strip(),
        previous_value=previous_value,
        proposed_value=proposed_value,
        evidence_refs=tuple(str(ref).strip() for ref in evidence_refs if str(ref).strip()),
        confidence=max(0.0, min(1.0, float(confidence))),
        risk=risk.strip().lower() or "low",
        rollback_value=previous_value,
        approved_by=approved_by,
    )


def validate_learning_proposal(
    proposal: LearningProposal,
    *,
    require_human_approval: bool | None = None,
    min_confidence: float | None = None,
) -> dict[str, Any]:
    require_human_approval = (
        REQUIRE_HUMAN_APPROVAL
        if require_human_approval is None
        else bool(require_human_approval)
    )
    min_confidence = (
        MIN_LEARNING_CONFIDENCE
        if min_confidence is None
        else float(min_confidence)
    )

    failures: list[str] = []
    if not proposal.key:
        failures.append("key_missing")
    if not proposal.evidence_refs:
        failures.append("evidence_missing")
    if proposal.confidence < min_confidence:
        failures.append("confidence_below_threshold")
    if require_human_approval and not proposal.approved_by:
        failures.append("human_approval_missing")

    return {
        "valid": not failures,
        "failures": failures,
        "commit_allowed": not failures,
    }
