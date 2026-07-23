from __future__ import annotations

from orion.contracts.models import EvolutionProposal


class EvolutionR20Adapter:
    """Converts the R20 EvolutionPlan contract into the Orion R25 proposal."""

    def from_r20(self, plan: object) -> EvolutionProposal:
        risk = plan.risk.to_dict() if hasattr(plan.risk, "to_dict") else dict(plan.risk)
        rollback = (
            plan.rollback.to_dict()
            if hasattr(plan.rollback, "to_dict")
            else dict(plan.rollback)
        )
        return EvolutionProposal(
            objective=plan.objective,
            files=list(plan.files),
            diff_preview=plan.diff_preview,
            tests=list(plan.tests),
            rollback=rollback,
            risk=risk,
            proposal_id=plan.proposal_id,
            status=plan.status,
            proposal_only=plan.proposal_only,
            requires_human_approval=plan.requires_human_approval,
            approved_by=plan.approved_by,
            approved_at=plan.approved_at,
            branch_name=plan.branch_name,
            metadata={"source_contract": "evolution_r20"},
        )
