from __future__ import annotations

from .models import GovernanceDecision, Proposal, utc_now_iso

OEP_001_GOVERNANCE_ENGINE_VERSION = "OEP_001_GOVERNANCE_ENGINE_V1"

class GovernanceEngine:
    def review(self, proposal: Proposal, *, human_approved: bool = False, approver: str | None = None) -> GovernanceDecision:
        required = []
        if not proposal.proposal_only:
            required.append("proposal_only_must_remain_true_until_approval")
        if proposal.write_executed:
            required.append("write_executed_must_be_false_before_execution")
        if proposal.human_approval_required and not human_approved:
            required.append("human_approval_required")
        if not proposal.rollback_plan:
            required.append("rollback_plan_required")
        if not proposal.tests:
            required.append("validation_tests_required")
        allowed = not required
        if allowed:
            proposal.status = "approved"
            proposal.approved_by = approver or "human"
            proposal.approved_at = utc_now_iso()
            proposal.touch()
        return GovernanceDecision(
            allowed=allowed,
            reason="approved_for_controlled_execution" if allowed else "blocked_by_governance_policy",
            proposal_id=proposal.proposal_id,
            required_actions=required,
            policy_version=OEP_001_GOVERNANCE_ENGINE_VERSION,
        )
