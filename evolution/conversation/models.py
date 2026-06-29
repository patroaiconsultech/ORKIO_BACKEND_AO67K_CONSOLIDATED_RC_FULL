from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass(frozen=True)
class ConversationMessage:
    role: str
    content: str
    message_id: str = field(default_factory=lambda: f"msg_{uuid4().hex[:16]}")
    created_at: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def normalized_content(self) -> str:
        return " ".join((self.content or "").split())

@dataclass(frozen=True)
class DistilledItem:
    item_type: str
    text: str
    confidence: float = 0.75
    source_message_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class DistillationResult:
    summary: str
    decisions: list[DistilledItem] = field(default_factory=list)
    actions: list[DistilledItem] = field(default_factory=list)
    bugs: list[DistilledItem] = field(default_factory=list)
    improvements: list[DistilledItem] = field(default_factory=list)
    ideas: list[DistilledItem] = field(default_factory=list)
    lessons: list[DistilledItem] = field(default_factory=list)
    risks: list[DistilledItem] = field(default_factory=list)
    confidence: float = 0.0
    created_at: str = field(default_factory=_utc_now)
    schema_version: str = "oep004.v1"
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def all_items(self) -> list[DistilledItem]:
        return [*self.decisions, *self.actions, *self.bugs, *self.improvements, *self.ideas, *self.lessons, *self.risks]

    def validate_governance(self) -> bool:
        if self.proposal_only is not True:
            raise ValueError("proposal_only must be True")
        if self.write_executed is not False:
            raise ValueError("write_executed must be False")
        if self.human_approval_required is not True:
            raise ValueError("human_approval_required must be True")
        return True

    def to_dict(self) -> dict[str, Any]:
        self.validate_governance()
        return asdict(self)
