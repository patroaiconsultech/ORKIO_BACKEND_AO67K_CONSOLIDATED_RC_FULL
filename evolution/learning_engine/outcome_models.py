from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class OutcomeRecord:
    proposal_id: str
    status: str
    score: float
    feedback: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    outcome_id: str = field(default_factory=lambda: f"out_{uuid4().hex[:16]}")
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not 0.0 <= float(data["score"]) <= 1.0:
            raise ValueError("Outcome score must be between 0.0 and 1.0")
        if data["proposal_only"] is not True:
            raise ValueError("proposal_only must remain True")
        if data["write_executed"] is not False:
            raise ValueError("write_executed must remain False")
        if data["human_approval_required"] is not True:
            raise ValueError("human_approval_required must remain True")
        return data
