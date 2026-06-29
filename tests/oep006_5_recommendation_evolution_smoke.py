from evolution.learning_engine import ExperienceRepository, RecommendationEvolution

repo = ExperienceRepository()
repo.add_experience(
    context="proposal ranking",
    proposal_id="prop_001",
    outcome_id="out_001",
    lesson="ranking with strong evidence succeeded",
    score=0.90,
    tags=["ranking"],
)
repo.add_experience(
    context="proposal ranking",
    proposal_id="prop_002",
    outcome_id="out_002",
    lesson="ranking with evidence succeeded again",
    score=0.80,
    tags=["ranking"],
)

evolution = RecommendationEvolution(repository=repo)
summary = evolution.summarize_pattern("ranking")

assert summary["matches"] == 2
assert summary["success_rate"] == 1.0
assert summary["recommendation"] == "repeat_pattern"
assert summary["proposal_only"] is True
assert summary["write_executed"] is False
assert summary["human_approval_required"] is True

print("OEP006_5_RECOMMENDATION_EVOLUTION_PASS")
