from __future__ import annotations
from typing import Any
from .proposal_models import ProposalEvidence, ProposalRisk

class ProposalAnalyzer:
    def analyze(self, knowledge_items: list[dict[str, Any]], objective: str) -> dict[str, Any]:
        objective = (objective or "").strip()
        if not objective:
            raise ValueError("objective is required")
        evidence = []
        source_documents = []
        for item in knowledge_items:
            doc_id = str(item.get("document_id") or item.get("id") or item.get("source_id") or "").strip()
            title = str(item.get("title") or "Knowledge item").strip()
            content = str(item.get("content") or item.get("text") or item.get("summary") or "").strip()
            if not content:
                continue
            evidence.append(ProposalEvidence(source_id=doc_id or title, title=title, excerpt=content[:280], score=float(item.get("score", 1.0) or 1.0), metadata=dict(item.get("metadata") or {})))
            if doc_id:
                source_documents.append(doc_id)
        if not evidence:
            raise ValueError("at least one knowledge item with content is required")
        risks = [ProposalRisk(level="low", description="Foundation proposal generated from deterministic knowledge analysis.", mitigation="Human approval remains mandatory before execution.")]
        confidence = min(0.95, 0.55 + (0.1 * min(len(evidence), 4)))
        return {"objective": objective, "evidence": evidence, "risks": risks, "confidence": round(confidence, 2), "source_documents": source_documents}
