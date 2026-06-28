from evolution.knowledge import create_knowledge_service

service = create_knowledge_service()

created = service.add_document(
    title="OEP003.2 Governance Smoke",
    content="Knowledge manifest governance operational",
    tags=["oep003", "manifest", "governance"],
)

assert created["proposal_only"] is True
assert created["write_executed"] is False
assert created["human_approval_required"] is True

documents = service.list_documents()
assert len(documents) == 1
assert documents[0]["document_id"] == created["document_id"]

results = service.search("governance")
assert len(results) >= 1
assert results[0]["proposal_only"] is True
assert results[0]["write_executed"] is False
assert results[0]["human_approval_required"] is True

manifest = service.manifest_entries()
assert len(manifest) == 1
assert manifest[0]["document_id"] == created["document_id"]
assert manifest[0]["proposal_only"] is True
assert manifest[0]["write_executed"] is False
assert manifest[0]["human_approval_required"] is True

assert service.validate_manifest() is True

print("OEP003_2_KNOWLEDGE_MANIFEST_GOVERNANCE_PASS")
