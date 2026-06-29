from evolution.learning_engine import ExperienceRepository

repo = ExperienceRepository()
experience = repo.add_experience(
    context="proposal ranking",
    proposal_id="prop_001",
    outcome_id="out_001",
    lesson="High confidence proposals with evidence performed well",
    score=0.88,
    tags=["proposal", "ranking", "evidence"],
)

assert experience["experience_id"]
assert experience["proposal_id"] == "prop_001"
assert experience["proposal_only"] is True
assert experience["write_executed"] is False
assert experience["human_approval_required"] is True

results = repo.search("evidence")
assert len(results) == 1
assert repo.list_experiences()[0]["score"] == 0.88

print("OEP006_4_EXPERIENCE_REPOSITORY_PASS")
