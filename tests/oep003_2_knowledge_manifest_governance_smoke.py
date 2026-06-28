from evolution.knowledge import create_knowledge_service

service = create_knowledge_service()

created = service.add_document(
    title="OEP003.2 Governance Smoke",
    content="Knowledge manifest governance operational",
    tags=["oep003", "manifest", "governance"],
)

documents = service.list_documents()
manifest = service.list_manifest()
results = service.search("governance")

assert created["id"]
assert created["manifest"]["document_id"] == created["id"]
assert created["manifest"]["proposal_only"] is True
assert created["manifest"]["write_executed"] is False
assert created["manifest"]["human_approval_required"] is True

assert len(documents) == 1
assert len(manifest) == 1
assert len(results) >= 1
assert service.validate_governance() is True

print("OEP003_2_KNOWLEDGE_MANIFEST_GOVERNANCE_PASS")
