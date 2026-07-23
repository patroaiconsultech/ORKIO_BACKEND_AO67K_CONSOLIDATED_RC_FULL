from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .premium_contracts import EvolutionPlan, RollbackPlan
from .premium_guard import ExecutionGateDecision, PremiumExecutionGuard
from .premium_risk import PremiumRiskEngine
from .premium_simulation import PremiumSimulationEngine


ORION_PREMIUM_PIPELINE_VERSION = "ORION_EVOLUTION_R20_PIPELINE_V1"


class OrionPremiumEvolutionPipeline:
    """
    Minimum-to-premium Orion evolution pipeline.

    State flow:
      proposal_only -> simulated -> approved_for_branch -> branch_gate_ready

    Safety properties:
      - no source write
      - no commit
      - no push
      - no deploy
      - production always forbidden
    """

    def __init__(self) -> None:
        self.risk_engine = PremiumRiskEngine()
        self.simulation_engine = PremiumSimulationEngine()
        self.execution_guard = PremiumExecutionGuard()

    def create_plan(
        self,
        *,
        objective: str,
        evidence: List[Dict[str, Any]],
        root_cause: str,
        files: List[str],
        diff_preview: str,
        rollback_strategy: str,
        rollback_commands: List[str],
        tests: List[str],
        declared_risk: Optional[str] = None,
        branch_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> EvolutionPlan:
        risk = self.risk_engine.assess(
            files=files,
            diff_preview=diff_preview,
            declared_risk=declared_risk,
        )
        rollback = RollbackPlan(
            strategy=rollback_strategy,
            commands=list(rollback_commands),
            verification_steps=list(tests),
        )
        return EvolutionPlan(
            objective=objective,
            evidence=list(evidence),
            root_cause=root_cause,
            files=list(files),
            diff_preview=diff_preview,
            risk=risk,
            rollback=rollback,
            tests=list(tests),
            branch_name=branch_name,
            metadata={
                "pipeline_version": ORION_PREMIUM_PIPELINE_VERSION,
                **(metadata or {}),
            },
        )

    def simulate(self, plan: EvolutionPlan, *, repo_root: str | Path | None = None):
        report = self.simulation_engine.run(plan, repo_root=repo_root)
        plan.simulation = report
        plan.status = "simulated" if report.passed else "simulation_blocked"
        return report

    def approve(self, plan: EvolutionPlan, *, approver: str) -> EvolutionPlan:
        if not plan.simulation or not plan.simulation.passed:
            raise ValueError("simulation_passed_required_before_approval")
        if not str(approver or "").strip():
            raise ValueError("named_human_approver_required")
        plan.approve(str(approver).strip())
        return plan

    def evaluate_branch_gate(
        self,
        plan: EvolutionPlan,
        *,
        requested_mode: str = "branch_dry_run",
    ) -> ExecutionGateDecision:
        decision = self.execution_guard.evaluate(
            plan,
            requested_mode=requested_mode,
            target_environment="branch",
        )
        if decision.allowed:
            plan.execution_mode = decision.mode
            plan.status = "branch_gate_ready"
        return decision

    def evaluate_production_gate(self, plan: EvolutionPlan) -> ExecutionGateDecision:
        return self.execution_guard.evaluate(
            plan,
            requested_mode="branch_apply",
            target_environment="production",
        )
