from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class PlannerProposalPackage:
    proposal_id: str
    title: str
    summary: str
    plan_id: str
    evidence: list[dict[str, Any]]
    risks: list[str]
    recommendation: str
    confidence: float
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PlannerProposalBridge:
    """Converts a planner output into a governed proposal package.

    This bridge prepares a proposal for human review. It does not execute plans.
    """

    def to_proposal(self, plan: Any, risk_assessment: dict[str, Any] | None = None, dependency_graph: dict[str, Any] | None = None) -> dict[str, Any]:
        data = plan.to_dict() if hasattr(plan, "to_dict") else dict(plan)
        risk_assessment = risk_assessment or {}
        dependency_graph = dependency_graph or {}

        plan_id = str(data.get("plan_id") or "")
        if not plan_id:
            raise ValueError("plan_id is required")

        risk_level = str(risk_assessment.get("risk_level") or "unknown")
        risks = list(risk_assessment.get("risk_factors") or [])
        if risk_level != "low":
            risks.append(f"risk_level:{risk_level}")

        package = PlannerProposalPackage(
            proposal_id="ppkg_" + uuid4().hex[:16],
            title=f"Planner proposal: {data.get('objective', 'Untitled plan')}",
            summary=data.get("summary", ""),
            plan_id=plan_id,
            evidence=[
                {"type": "plan", "plan_id": plan_id},
                {"type": "risk_assessment", "risk_level": risk_level, "risk_score": risk_assessment.get("risk_score")},
                {"type": "dependency_graph", "nodes": len(dependency_graph.get("nodes", [])), "edges": len(dependency_graph.get("edges", []))},
            ],
            risks=sorted(set(risks)),
            recommendation="submit_for_human_review",
            confidence=float(data.get("confidence", 0.0)),
        )
        return package.to_dict()
