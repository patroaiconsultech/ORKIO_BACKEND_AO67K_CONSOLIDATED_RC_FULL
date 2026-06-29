from __future__ import annotations
from typing import Protocol
from .models import ConversationMessage, DistillationResult

class ConversationDistillerContract(Protocol):
    def distill(self, conversation: str | list[ConversationMessage]) -> DistillationResult:
        ...
