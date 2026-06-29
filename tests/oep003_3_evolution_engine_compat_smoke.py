from evolution.engine import EvolutionEngine
from evolution.knowledge import KnowledgeEngine, create_knowledge_service
from evolution.knowledge_manifest import KNOWLEDGE_MODULE_MANIFEST


engine = EvolutionEngine()

assert isinstance(engine.knowledge, KnowledgeEngine)
assert KNOWLEDGE_MODULE_MANIFEST["write_executed"] is False
assert "chat" in KNOWLEDGE_MODULE_MANIFEST["excluded_scope"]

service = create_knowledge_service()
created = service.add_document(
    title="OEP003.3 Compatibility Smoke",
    content="EvolutionEngine compatibility and governance stabilization operational",
    tags=["oep003.3", "compat"],
)

assert created["proposal_only"] is True
assert created["write_executed"] is False
assert created["human_approval_required"] is True
assert service.validate_governance() is True
assert service.search("compatibility")

print("OEP003_3_EVOLUTION_ENGINE_COMPAT_PASS")
