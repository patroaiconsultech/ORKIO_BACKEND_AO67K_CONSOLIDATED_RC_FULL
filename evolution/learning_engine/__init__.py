from evolution.learning_engine.memory import LearningMemory, LearningMemoryRecord
from evolution.learning_engine.service import LearningService, learning_service
from evolution.learning_engine.outcome_models import OutcomeRecord
from evolution.learning_engine.outcome_tracker import OutcomeTracker
from evolution.learning_engine.confidence_calibration import ConfidenceCalibrator
from evolution.learning_engine.experience_repository import ExperienceRecord, ExperienceRepository
from evolution.learning_engine.recommendation_evolution import RecommendationEvolution


class LearningEngineService(LearningService):
    def extract_from_proposals(self, proposals):
        signals = []
        for proposal in proposals:
            confidence = float(proposal.get("confidence", 0.0))
            if confidence < 0.80:
                continue
            signals.append({
                "category": "high_confidence_proposal",
                "proposal_id": proposal.get("proposal_id"),
                "title": proposal.get("title", ""),
                "confidence": confidence,
                "proposal_only": True,
                "write_executed": False,
                "human_approval_required": True,
            })
        return signals


__all__ = [
    "LearningMemory",
    "LearningMemoryRecord",
    "LearningService",
    "LearningEngineService",
    "learning_service",
    "OutcomeRecord",
    "OutcomeTracker",
    "ConfidenceCalibrator",
    "ExperienceRecord",
    "ExperienceRepository",
    "RecommendationEvolution",
]
