from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import time
import uuid


@dataclass(frozen=True)
class KnowledgeSource:
    source_id: str
    source_type: str
    title: str
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeItem:
    content: str
    category: str
    source_id: str
    item_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    confidence: float = 0.75
    tags: List[str] = field(default_factory=list)
    canonical: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
