from __future__ import annotations

from evolution.autonomous_planner.models import AutonomousPlan


class AutonomousPlannerRepository:
    def __init__(self) -> None:
        self._plans: dict[str, AutonomousPlan] = {}

    def save(self, plan: AutonomousPlan) -> dict:
        plan.validate_governance()
        self._plans[plan.plan_id] = plan
        return plan.to_dict()

    def get(self, plan_id: str) -> dict | None:
        plan = self._plans.get(plan_id)
        return plan.to_dict() if plan else None

    def list(self) -> list[dict]:
        return [plan.to_dict() for plan in self._plans.values()]
