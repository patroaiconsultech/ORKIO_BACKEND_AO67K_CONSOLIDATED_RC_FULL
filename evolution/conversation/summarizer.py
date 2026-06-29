from __future__ import annotations
from .models import ConversationMessage

class DeterministicConversationSummarizer:
    def summarize(self, messages: list[ConversationMessage], max_chars: int = 280) -> str:
        if not messages:
            return "Empty conversation."
        summary = " | ".join(f"{m.role}: {m.normalized_content()}" for m in messages[:6] if m.normalized_content())
        return summary if len(summary) <= max_chars else summary[:max_chars-3].rstrip() + "..."
