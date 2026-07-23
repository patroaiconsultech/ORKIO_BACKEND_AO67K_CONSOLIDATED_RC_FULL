from __future__ import annotations


class PriorityEngine:
    def score(
        self,
        *,
        expected_value: float,
        urgency: int,
        confidence: float,
        risk_score: int,
    ) -> float:
        urgency_factor = max(0, min(10, urgency)) / 10
        confidence_factor = max(0.0, min(1.0, confidence))
        risk_penalty = max(0, min(100, risk_score)) / 100
        return round(
            (expected_value * 0.45) +
            (urgency_factor * 100 * 0.25) +
            (confidence_factor * 100 * 0.30) -
            (risk_penalty * 35),
            2,
        )
