from evolution.learning_engine import OutcomeTracker

tracker = OutcomeTracker()
outcome = tracker.record_outcome(
    proposal_id="prop_001",
    status="approved",
    score=0.91,
    feedback="Proposal produced useful result",
)

assert outcome["outcome_id"]
assert outcome["proposal_id"] == "prop_001"
assert outcome["score"] == 0.91
assert outcome["proposal_only"] is True
assert outcome["write_executed"] is False
assert outcome["human_approval_required"] is True

records = tracker.get_by_proposal("prop_001")
assert len(records) == 1
assert tracker.average_score() == 0.91

print("OEP006_2_OUTCOME_TRACKER_PASS")
