from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import List

from .premium_contracts import EvolutionPlan


@dataclass(frozen=True)
class ExecutionGateDecision:
    allowed: bool
    mode: str
    reasons: List[str]


class PremiumExecutionGuard:
    """
    Final governance gate.

    R20 deliberately does not implement a writer. It only decides whether a
    separately implemented branch executor could be called.
    """

    _BRANCH_PATTERN = re.compile(r"^(orion|evolution|patch)/[a-z0-9._-]+$")

    def evaluate(
        self,
        plan: EvolutionPlan,
        *,
        requested_mode: str = "branch_dry_run",
        target_environment: str = "branch",
    ) -> ExecutionGateDecision:
        reasons: List[str] = []
        mode = str(requested_mode or "none").strip().lower()
        environment = str(target_environment or "branch").strip().lower()

        if not plan.proposal_only:
            reasons.append("proposal_only_contract_broken")
        if not plan.requires_human_approval:
            reasons.append("human_approval_contract_missing")
        if not plan.approved_by:
            reasons.append("human_approval_missing")
        if not plan.simulation or not plan.simulation.passed:
            reasons.append("simulation_not_passed")
        if plan.write_executed:
            reasons.append("write_already_executed")
        if not plan.rollback.strategy or not plan.rollback.commands:
            reasons.append("rollback_incomplete")
        if not plan.tests:
            reasons.append("validation_tests_missing")
        if plan.risk.level == "high":
            reasons.append("high_risk_requires_manual_release_board")
        if environment in {"production", "prod"}:
            reasons.append("production_execution_forbidden")
        if mode not in {"branch_dry_run", "branch_apply"}:
            reasons.append("unsupported_execution_mode")

        branch = str(plan.branch_name or "")
        if not branch or not self._BRANCH_PATTERN.match(branch):
            reasons.append("invalid_or_missing_isolated_branch")

        feature_flag = os.getenv("ORION_BRANCH_EXECUTION_ENABLED", "false").strip().lower()
        if mode == "branch_apply" and feature_flag not in {"1", "true", "yes", "on"}:
            reasons.append("branch_execution_feature_flag_disabled")

        return ExecutionGateDecision(
            allowed=not reasons,
            mode=mode,
            reasons=sorted(set(reasons)),
        )
