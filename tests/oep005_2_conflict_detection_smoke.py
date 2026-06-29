from evolution.proposal_engine.conflicts import ProposalConflictDetector

detector = ProposalConflictDetector()
conflicts = detector.detect([
    {"proposal_id": "p1", "title": "Fix Knowledge Contract"},
    {"proposal_id": "p2", "title": "Fix Knowledge Contract"},
])

assert len(conflicts) == 1
assert conflicts[0]["type"] == "duplicate_title"
assert conflicts[0]["proposal_only"] is True
assert conflicts[0]["requires_human_approval"] is True
print("OEP005_2_CONFLICT_DETECTION_PASS")
