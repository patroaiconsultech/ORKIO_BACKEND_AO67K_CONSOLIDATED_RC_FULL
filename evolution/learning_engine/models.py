from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class LearningSignal:
    signal_id: str = field(default_factory=lambda: f"lsig_{uuid4().hex[:16]}")
    source: str = "proposal_engine"
    category: str = "pattern"
    summary: str = ""
    confidence: float = 0.0
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
