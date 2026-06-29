from __future__ import annotations

from typing import Any

from evolution.conversation.models import DistillationResult


def result_to_knowledge_documents(result: DistillationResult) -> list[dict[str, Any]]:
    """
    Convert a DistillationResult into governance-safe knowledge documents.

    OEP-004.1 intentionally does not write to KnowledgeService.
    It only prepares proposal_only payloads for a later approved integration.
    """
    documents: list[dict[str, Any]] = []

    summary = getattr(result, "summary", "") or ""
    if summary.strip():
        documents.append(
            {
                "title": "Conversation summary",
                "content": summary.strip(),
                "tags": ["conversation", "summary", "oep004"],
                "source": "conversation_distiller",
                "scope": "general",
                "proposal_only": True,
                "write_executed": False,
                "human_approval_required": True,
                "metadata": {"distillation_type": "summary"},
            }
        )

    buckets = [
        ("decision", getattr(result, "decisions", [])),
        ("action", getattr(result, "actions", [])),
        ("bug", getattr(result, "bugs", [])),
        ("idea", getattr(result, "ideas", [])),
        ("lesson", getattr(result, "lessons", [])),
        ("risk", getattr(result, "risks", [])),
    ]

    for bucket_name, items in buckets:
        for item in items:
            text = getattr(item, "text", None) or str(item)
            if not text.strip():
                continue
            documents.append(
                {
                    "title": f"Conversation {bucket_name}",
                    "content": text.strip(),
                    "tags": ["conversation", bucket_name, "oep004"],
                    "source": "conversation_distiller",
                    "scope": "general",
                    "proposal_only": True,
                    "write_executed": False,
                    "human_approval_required": True,
                    "metadata": {
                        "distillation_type": bucket_name,
                        "confidence": getattr(item, "confidence", None),
                    },
                }
            )

    return documents
