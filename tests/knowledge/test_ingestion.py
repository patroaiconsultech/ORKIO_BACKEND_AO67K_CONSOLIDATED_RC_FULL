from app.knowledge.ingestion import KnowledgeIngestionService
from app.knowledge.schema import KnowledgeSource
from app.knowledge.source_registry import KnowledgeSourceRegistry
from app.knowledge.store import InMemoryKnowledgeStore


def test_ingestion_classifies_orkio_conversation():
    store = InMemoryKnowledgeStore()
    sources = KnowledgeSourceRegistry()
    service = KnowledgeIngestionService(store=store, source_registry=sources)

    source = KnowledgeSource(
        source_id="gpt-conversation-001",
        source_type="gpt_export",
        title="Conversa Orkio CTO",
    )

    item = service.ingest_text(
        source,
        "Orkio deve evoluir com Cognitive Kernel, agentes, backend FastAPI e SSE.",
        canonical=True,
    )

    assert item.category == "technical_architecture"
    assert item.canonical is True
    assert "orkio" in item.tags
    assert len(store.all()) == 1


def test_store_search_text():
    store = InMemoryKnowledgeStore()
    sources = KnowledgeSourceRegistry()
    service = KnowledgeIngestionService(store=store, source_registry=sources)

    source = KnowledgeSource(source_id="src", source_type="manual", title="Manual")
    service.ingest_text(source, "Daniel é Superadmin da PatroAI.", canonical=True)

    results = store.search_text("Superadmin")

    assert len(results) == 1
    assert results[0].category == "canonical_identity"
