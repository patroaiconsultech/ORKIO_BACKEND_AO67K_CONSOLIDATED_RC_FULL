from __future__ import annotations

from evolution.autonomous_planner.planner import AutonomousPlanner
from evolution.autonomous_planner.repository import AutonomousPlannerRepository
from evolution.autonomous_planner.validator import AutonomousPlanValidator


class PlanPayload(dict):
    """Dict-compatible payload with attribute access for planner compatibility."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


class AutonomousPlannerService:
    def __init__(
        self,
        planner: AutonomousPlanner | None = None,
        repository: AutonomousPlannerRepository | None = None,
        validator: AutonomousPlanValidator | None = None,
    ) -> None:
        self._planner = planner or AutonomousPlanner()
        self._repository = repository or AutonomousPlannerRepository()
        self._validator = validator or AutonomousPlanValidator()

    def create_plan(self, objective: str, context: list[dict] | str | None = None) -> PlanPayload:
        plan = self._planner.create_plan(objective=objective, context=context)
        payload = self._repository.save(plan)
        self._validator.validate(payload)
        return PlanPayload(payload)

    def list_plans(self) -> list[dict]:
        return self._repository.list()

    def validate_plan(self, plan: dict) -> bool:
        return self._validator.validate(plan)


autonomous_planner_service = AutonomousPlannerService()
