from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass(frozen=True)
class PlanRiskAssessment:
    risk_score: float
    risk_level: str
    risk_factors: list[str] = field(default_factory=list)
    requires_review: bool = True
    rollback_required: bool = True
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PlanRiskScorer:
    """Deterministic risk scorer for autonomous planner proposals.

    This module does not execute any plan. It only classifies risk and preserves
    governance flags for human approval workflows.
    """

    HIGH_TERMS = ("database", "migration", "delete", "remove", "drop", "production", "deploy", "auth", "security")
    MEDIUM_TERMS = ("api", "schema", "integration", "stream", "realtime", "cache", "rollback", "dependency")

    def score(self, plan: Any) -> dict[str, Any]:
        data = plan.to_dict() if hasattr(plan, "to_dict") else dict(plan)
        objective = str(data.get("objective", "")).lower()
        summary = str(data.get("summary", "")).lower()
        steps = data.get("steps", []) or []

        text = " ".join([objective, summary] + [
            " ".join([
                str(step.get("title", "")),
                str(step.get("action", "")),
                str(step.get("rationale", "")),
                str(step.get("risk", "")),
            ]).lower()
            for step in steps
            if isinstance(step, dict)
        ])

        factors: list[str] = []
        score = 0.10

        if len(steps) >= 4:
            score += 0.15
            factors.append("multi_step_plan")

        for term in self.MEDIUM_TERMS:
            if term in text:
                score += 0.08
                factors.append(f"medium_term:{term}")

        for term in self.HIGH_TERMS:
            if term in text:
                score += 0.15
                factors.append(f"high_term:{term}")

        if any(isinstance(step, dict) and str(step.get("risk", "")).lower() == "high" for step in steps):
            score += 0.25
            factors.append("explicit_high_risk_step")

        score = round(max(0.0, min(1.0, score)), 2)

        if score >= 0.70:
            level = "high"
        elif score >= 0.35:
            level = "medium"
        else:
            level = "low"

        assessment = PlanRiskAssessment(
            risk_score=score,
            risk_level=level,
            risk_factors=sorted(set(factors)),
            requires_review=True,
            rollback_required=level in ("medium", "high"),
        )
        return assessment.to_dict()
