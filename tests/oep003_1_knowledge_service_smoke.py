from evolution.knowledge import create_knowledge_service
from evolution.knowledge_manifest import KNOWLEDGE_MODULE_MANIFEST


service = create_knowledge_service()

created = service.add_document(
    title="OEP003.1 Service Layer",
    content="Knowledge service layer operational and decoupled",
    tags=["oep003.1", "service"],
)

results = service.search("decoupled")
documents = service.list_documents()

assert created["id"]
assert results
assert results[0]["title"] == "OEP003.1 Service Layer"
assert len(documents) == 1
assert KNOWLEDGE_MODULE_MANIFEST["oep"] == "003.1"
assert KNOWLEDGE_MODULE_MANIFEST["write_executed"] is False
assert "chat" in KNOWLEDGE_MODULE_MANIFEST["excluded_scope"]

print("OEP003_1_KNOWLEDGE_SERVICE_LAYER_PASS")
