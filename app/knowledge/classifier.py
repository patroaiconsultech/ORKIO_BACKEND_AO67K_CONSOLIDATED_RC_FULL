from __future__ import annotations

from typing import List


class KnowledgeClassifier:
    """Rule-based starter classifier for GPT conversation imports.

    This is deterministic and safe for tests. Later it can be replaced by an LLM
    classifier through the plugin registry.
    """

    def classify(self, text: str) -> dict:
        lower = text.lower()
        tags: List[str] = []

        if any(term in lower for term in ["orkio", "kernel", "agente", "sse", "backend", "frontend"]):
            category = "technical_architecture"
            tags.append("orkio")
        elif any(term in lower for term in ["fintegra", "investidor", "captação", "captacao", "business plan"]):
            category = "business_strategy"
            tags.append("business")
        elif any(term in lower for term in ["daniel", "superadmin", "patroai", "holding"]):
            category = "canonical_identity"
            tags.append("identity")
        else:
            category = "general_knowledge"

        return {
            "category": category,
            "tags": tags,
            "confidence": 0.78 if category != "general_knowledge" else 0.55,
        }
