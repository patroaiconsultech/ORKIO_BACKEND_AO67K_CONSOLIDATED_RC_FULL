from __future__ import annotations

from evolution.autonomous_planner.models import AutonomousPlan, PlanStep, new_plan_id, new_step_id


class AutonomousPlanner:
    def create_plan(self, objective: str, context: list[dict] | None = None) -> AutonomousPlan:
        clean_objective = (objective or "").strip()
        if not clean_objective:
            raise ValueError("objective is required")

        context = context or []
        signals = [item for item in context if isinstance(item, dict)]
        confidence_values = [
            float(item.get("confidence", 0.0))
            for item in signals
            if item.get("confidence") is not None
        ]
        confidence = round(sum(confidence_values) / len(confidence_values), 4) if confidence_values else 0.5

        steps = [
            PlanStep(
                step_id=new_step_id(),
                title="Review evidence",
                action="review_evidence",
                rationale="Validate available knowledge, proposals, and learning signals before any change.",
                risk="low",
            ),
            PlanStep(
                step_id=new_step_id(),
                title="Draft proposal",
                action="draft_proposal",
                rationale="Prepare a proposal-only recommendation for human review.",
                risk="low",
            ),
            PlanStep(
                step_id=new_step_id(),
                title="Request human approval",
                action="request_human_approval",
                rationale="No execution is allowed without explicit human approval.",
                risk="low",
            ),
        ]

        plan = AutonomousPlan(
            plan_id=new_plan_id(),
            objective=clean_objective,
            summary=f"Proposal-only autonomous plan for: {clean_objective}",
            steps=steps,
            confidence=confidence,
            metadata={"context_items": len(signals)},
        )
        plan.validate_governance()
        return plan
