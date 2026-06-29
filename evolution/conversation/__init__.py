from evolution.conversation.batch import ConversationBatchProcessor, BatchDistillationReport
from evolution.conversation.distiller import ConversationDistiller
from evolution.conversation.idempotency import make_idempotency_key, normalize_conversation_text

__all__ = [
    "BatchDistillationReport",
    "ConversationBatchProcessor",
    "ConversationDistiller",
    "make_idempotency_key",
    "normalize_conversation_text",
]

# Backward-compatible facade for OEP-004 smoke
def distill_conversation(conversation: str):
    return ConversationDistiller().distill(conversation)
