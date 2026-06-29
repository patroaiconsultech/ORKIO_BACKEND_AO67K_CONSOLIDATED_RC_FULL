from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class PlanStep:
    step_id: str
    title: str
    action: str
    rationale: str
    risk: str = "low"
    status: str = "proposed"
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AutonomousPlan:
    plan_id: str
    objective: str
    summary: str
    steps: list[PlanStep]
    confidence: float
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate_governance(self) -> bool:
        if self.proposal_only is not True:
            raise ValueError("proposal_only must be True")
        if self.write_executed is not False:
            raise ValueError("write_executed must be False")
        if self.human_approval_required is not True:
            raise ValueError("human_approval_required must be True")
        for step in self.steps:
            if step.proposal_only is not True:
                raise ValueError("step proposal_only must be True")
            if step.write_executed is not False:
                raise ValueError("step write_executed must be False")
            if step.human_approval_required is not True:
                raise ValueError("step human_approval_required must be True")
        return True

    def to_dict(self) -> dict[str, Any]:
        self.validate_governance()
        data = asdict(self)
        data["steps"] = [step.to_dict() for step in self.steps]
        return data


def new_plan_id() -> str:
    return "plan_" + uuid4().hex[:16]


def new_step_id() -> str:
    return "step_" + uuid4().hex[:16]
