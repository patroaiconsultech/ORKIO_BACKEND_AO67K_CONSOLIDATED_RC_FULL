from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class KnowledgeItem:
    source_id: str
    name: str
    mime_type: str = ""
    path: str = ""
    metadata: Dict[str, Any] | None = None

@dataclass
class ClassificationResult:
    domain: str
    sensitivity: str
    runtime_allowed: bool
    requires_human_approval: bool
    reason: str
