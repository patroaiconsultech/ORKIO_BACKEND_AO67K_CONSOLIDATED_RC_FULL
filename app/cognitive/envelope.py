from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import time
import uuid


@dataclass
class DecisionEnvelope:
    """Auditable decision artifact produced by the Cognitive Microkernel."""

    request_id: str
    tenant_id: str
    user_id: str
    envelope_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mode: str = "shadow"
    intent: Optional[str] = None
    confidence: float = 0.0
    category: Optional[str] = None
    complexity: str = "unknown"
    runtime: Optional[str] = None
    executor: Optional[str] = None
    policy_status: str = "unknown"
    risk_level: str = "unknown"
    proposal_only: bool = True
    plan: List[Dict[str, Any]] = field(default_factory=list)
    plugin_results: List[Dict[str, Any]] = field(default_factory=list)
    observations: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
