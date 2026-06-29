from __future__ import annotations

from dataclasses import asdict
from typing import Any

from evolution.learning_engine.models import LearningSignal


class LearningEngineService:
    """OEP-006 foundation: extract non-executing learning signals."""

    def extract_from_proposals(self, proposals: list[dict[str, Any]]) -> list[dict[str, Any]]:
        signals: list[dict[str, Any]] = []
        for proposal in proposals:
            confidence = float(proposal.get("confidence", 0.0) or 0.0)
            if confidence >= 0.75:
                signals.append(asdict(LearningSignal(
                    category="high_confidence_proposal",
                    summary=str(proposal.get("title") or "Untitled proposal"),
                    confidence=confidence,
                )))
        return signals
