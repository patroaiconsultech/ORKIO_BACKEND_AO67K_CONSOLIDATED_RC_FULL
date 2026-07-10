from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class ExecutivePreflightResult:
    version: str
    applies: bool
    intent: str
    confidence: float
    required_outputs: List[str] = field(default_factory=list)
    block_public_journey_fastpath: bool = False
    quality_mode: str = "standard"
    reason: str = "not_executive"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExecutiveReleaseResult:
    version: str
    applies: bool
    release: bool
    final_text: str
    score: int
    missing_outputs: List[str] = field(default_factory=list)
    retry_performed: bool = False
    retry_count: int = 0
    reason: str = "not_applicable"
    validation: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
