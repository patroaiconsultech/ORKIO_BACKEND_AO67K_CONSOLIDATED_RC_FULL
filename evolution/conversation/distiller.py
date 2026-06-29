from __future__ import annotations
from .classifier import RuleBasedConversationClassifier
from .models import ConversationMessage, DistilledItem, DistillationResult
from .repository import InMemoryDistillationRepository
from .summarizer import DeterministicConversationSummarizer

class ConversationDistiller:
    def __init__(self, classifier: RuleBasedConversationClassifier | None = None, summarizer: DeterministicConversationSummarizer | None = None, repository: InMemoryDistillationRepository | None = None) -> None:
        self._classifier = classifier or RuleBasedConversationClassifier()
        self._summarizer = summarizer or DeterministicConversationSummarizer()
        self._repository = repository

    def distill(self, conversation: str | list[ConversationMessage]) -> DistillationResult:
        messages = self._normalize(conversation)
        buckets = {k: [] for k in ("decisions","actions","bugs","improvements","ideas","lessons","risks")}
        for message in messages:
            for key, items in self._classifier.classify_message(message).items():
                buckets[key].extend(items)
        all_items = [item for items in buckets.values() for item in items]
        result = DistillationResult(
            summary=self._summarizer.summarize(messages),
            decisions=buckets["decisions"], actions=buckets["actions"], bugs=buckets["bugs"],
            improvements=buckets["improvements"], ideas=buckets["ideas"], lessons=buckets["lessons"], risks=buckets["risks"],
            confidence=self._calculate_confidence(all_items),
            metadata={"message_count": len(messages), "distiller": "rule_based_v1", "llm_used": False},
        )
        result.validate_governance()
        if self._repository is not None:
            self._repository.add(result)
        return result

    @staticmethod
    def _normalize(conversation: str | list[ConversationMessage]) -> list[ConversationMessage]:
        if isinstance(conversation, str):
            lines = [line.strip() for line in conversation.splitlines() if line.strip()]
            if not lines and conversation.strip():
                lines = [conversation.strip()]
            return [ConversationMessage(role="unknown", content=line) for line in lines]
        return [m for m in conversation if m.normalized_content()]

    @staticmethod
    def _calculate_confidence(items: list[DistilledItem]) -> float:
        return 0.0 if not items else round(sum(i.confidence for i in items) / len(items), 4)

def distill_conversation(conversation: str | list[ConversationMessage]) -> DistillationResult:
    return ConversationDistiller().distill(conversation)
