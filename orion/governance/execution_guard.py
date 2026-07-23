from __future__ import annotations

import re

from orion.contracts.models import EvolutionProposal, GovernanceDecision, PatchArtifact
from .permission_matrix import PermissionMatrix


class ExecutionGuard:
    BRANCH_RE = re.compile(r"^(orion|evolution|patch)/[a-z0-9._-]+$")

    def __init__(self, permissions: PermissionMatrix | None = None) -> None:
        self.permissions = permissions or PermissionMatrix()

    def evaluate_branch_execution(
        self,
        proposal: EvolutionProposal,
        patch: PatchArtifact,
        *,
        target_environment: str = "sandbox",
    ) -> GovernanceDecision:
        reasons: list[str] = []
        if target_environment.lower() in {"production", "prod"}:
            reasons.append("production_execution_forbidden")
        if not proposal.proposal_only:
            reasons.append("proposal_only_contract_broken")
        if not proposal.requires_human_approval:
            reasons.append("human_approval_contract_missing")
        if not proposal.approved_by:
            reasons.append("human_approval_missing")
        if proposal.risk.get("level") == "high":
            reasons.append("high_risk_requires_manual_release_board")
        if not proposal.rollback.get("strategy"):
            reasons.append("rollback_missing")
        if not proposal.tests:
            reasons.append("tests_missing")
        if not proposal.branch_name or not self.BRANCH_RE.match(proposal.branch_name):
            reasons.append("invalid_isolated_branch")
        if patch.proposal_id != proposal.proposal_id:
            reasons.append("patch_proposal_mismatch")
        if set(patch.files_changed) != set(proposal.files):
            reasons.append("patch_scope_mismatch")
        if not self.permissions.allows("execution", "write_sandbox"):
            reasons.append("sandbox_write_permission_missing")

        return GovernanceDecision(
            allowed=not reasons,
            action="execute_in_sandbox",
            reasons=sorted(set(reasons)),
        )

    def evaluate_production(self) -> GovernanceDecision:
        return GovernanceDecision(
            allowed=False,
            action="deploy_production",
            reasons=["production_execution_forbidden"],
        )
