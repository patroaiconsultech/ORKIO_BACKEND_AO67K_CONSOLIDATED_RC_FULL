from evolution.proposal_engine.ranking import ProposalRanker

ranker = ProposalRanker()
ranked = ranker.rank([
    {"proposal_id": "p1", "title": "Low", "confidence": 0.5, "evidence": ["a"], "risks": ["r"], "proposal_only": True, "requires_human_approval": True},
    {"proposal_id": "p2", "title": "High", "confidence": 0.9, "evidence": ["a", "b"], "risks": [], "proposal_only": True, "requires_human_approval": True},
])

assert ranked[0]["proposal_id"] == "p2"
assert ranked[0]["ranking_score"] > ranked[1]["ranking_score"]
print("OEP005_1_PROPOSAL_RANKING_PASS")
