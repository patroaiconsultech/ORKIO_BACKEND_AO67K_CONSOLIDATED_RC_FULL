from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4


@dataclass(frozen=True)
class DecisionReceipt:
    trace_id: str
    message_id: str
    thread_id: str
    architecture: Dict[str, Any]
    attachment_resolution: Dict[str, Any]
    execution_profile: Dict[str, Any]
    agent_authority: Dict[str, Any]
    blocked_actions: List[str] = field(default_factory=list)
    divergences: List[str] = field(default_factory=list)
    shadow_mode: bool = True
    enforcement: bool = False
    write_executed: bool = False
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    receipt_id: str = field(default_factory=lambda: f"ocil_{uuid4().hex}")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)
