from __future__ import annotations


class ConfidenceCalibrator:
    def calibrate(self, base_confidence: float, outcomes: list[dict]) -> dict:
        base = max(0.0, min(1.0, float(base_confidence)))
        scores = [float(item.get("score", 0.0)) for item in outcomes]
        if scores:
            outcome_mean = round(sum(scores) / len(scores), 2)
            calibrated = (base * 0.6) + (outcome_mean * 0.4)
        else:
            outcome_mean = 0.0
            calibrated = base

        calibrated = round(max(0.0, min(1.0, calibrated)), 4)
        return {
            "base_confidence": base,
            "outcome_mean": outcome_mean,
            "calibrated_confidence": calibrated,
            "sample_size": len(scores),
            "proposal_only": True,
            "write_executed": False,
            "human_approval_required": True,
        }
