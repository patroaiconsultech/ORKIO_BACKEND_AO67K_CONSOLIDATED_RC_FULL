from evolution.learning_engine import LearningEngineService

service = LearningEngineService()
signals = service.extract_from_proposals([
    {"proposal_id": "p1", "title": "Strong pattern", "confidence": 0.88},
    {"proposal_id": "p2", "title": "Weak pattern", "confidence": 0.44},
])

assert len(signals) == 1
assert signals[0]["category"] == "high_confidence_proposal"
assert signals[0]["proposal_only"] is True
assert signals[0]["write_executed"] is False
assert signals[0]["human_approval_required"] is True
print("OEP006_LEARNING_ENGINE_FOUNDATION_PASS")
