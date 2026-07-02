from dataclasses import dataclass, field
from typing import Any, Dict, List
from uuid import uuid4

@dataclass
class Classification:
    category: str
    confidence: float
    matched: List[str] = field(default_factory=list)

@dataclass
class KernelInput:
    message: str
    user_context: Dict[str, Any] = field(default_factory=dict)
    thread_context: Dict[str, Any] = field(default_factory=dict)
    capability_registry: Dict[str, Any] = field(default_factory=dict)
    governance_policy: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KernelResult:
    handled: bool
    assistant_turn_id: str
    response_text: str
    classification: Classification
    truth_labels: List[str]
    governance_flags: Dict[str, Any]
    capability_references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

def new_turn_id() -> str:
    return uuid4().hex
