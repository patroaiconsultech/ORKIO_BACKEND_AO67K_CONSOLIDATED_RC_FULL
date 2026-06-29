from __future__ import annotations

from typing import Any


REQUIRED_PLAN_FIELDS = (
    "plan_id",
    "steps",
    "risk_level",
    "dependencies",
    "rollback",
)


class PlannerSafetyError(ValueError):
    pass


class PlannerSafetyGate:
    """Deterministic safety gate for autonomous planning.

    This module does not execute plans. It only validates and normalizes plan
    payloads so downstream modules can keep human approval as the final gate.
    """

    def validate(self, plan: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(plan, dict):
            raise PlannerSafetyError("plan must be a dict")

        missing = [field for field in REQUIRED_PLAN_FIELDS if field not in plan]
        if missing:
            raise PlannerSafetyError(f"missing required plan fields: {', '.join(missing)}")

        steps = plan.get("steps")
        if not isinstance(steps, list) or not steps:
            raise PlannerSafetyError("steps must be a non-empty list")

        rollback = plan.get("rollback")
        if not isinstance(rollback, str) or not rollback.strip():
            raise PlannerSafetyError("rollback must be a non-empty string")

        dependencies = plan.get("dependencies")
        if dependencies is None:
            dependencies = []
        if not isinstance(dependencies, list):
            raise PlannerSafetyError("dependencies must be a list")

        safe_plan = dict(plan)
        safe_plan["dependencies"] = dependencies
        safe_plan["approval_required"] = True
        safe_plan["proposal_only"] = True
        safe_plan["write_executed"] = False
        safe_plan["human_approval_required"] = True
        safe_plan["execution_allowed"] = False
        return safe_plan


planner_safety_gate = PlannerSafetyGate()
