from evolution.proposal_engine import create_proposal_service

service = create_proposal_service()
knowledge_items = [{
    "id": "kdoc_oep005_smoke",
    "document_id": "kdoc_oep005_smoke",
    "title": "OEP-005 Smoke Knowledge",
    "content": "Proposal Engine should transform knowledge into governed proposal packages.",
    "tags": ["oep005", "proposal"],
    "metadata": {"source": "smoke"},
}]
proposal = service.create_proposal(knowledge_items=knowledge_items, objective="Create a governed proposal from structured knowledge")

assert proposal["proposal_id"].startswith("proposal_")
assert proposal["title"]
assert proposal["summary"]
assert proposal["recommendation"]
assert len(proposal["evidence"]) >= 1
assert 0.0 <= proposal["confidence"] <= 1.0
assert proposal["proposal_only"] is True
assert proposal["requires_human_approval"] is True
assert proposal["write_executed"] is False
assert len(service.list_proposals()) == 1

print("OEP005_PROPOSAL_ENGINE_FOUNDATION_PASS")
