from __future__ import annotations

from typing import Iterable, List

from .classifier import KnowledgeClassifier
from .schema import KnowledgeItem, KnowledgeSource
from .source_registry import KnowledgeSourceRegistry
from .store import InMemoryKnowledgeStore
from .summarizer import ExtractiveSummarizer


class KnowledgeIngestionService:
    """Transforms raw GPT conversations into structured knowledge items."""

    def __init__(
        self,
        store: InMemoryKnowledgeStore,
        source_registry: KnowledgeSourceRegistry,
        classifier: KnowledgeClassifier | None = None,
        summarizer: ExtractiveSummarizer | None = None,
    ) -> None:
        self.store = store
        self.source_registry = source_registry
        self.classifier = classifier or KnowledgeClassifier()
        self.summarizer = summarizer or ExtractiveSummarizer()

    def ingest_text(
        self,
        source: KnowledgeSource,
        text: str,
        canonical: bool = False,
    ) -> KnowledgeItem:
        if not self.source_registry.get(source.source_id):
            self.source_registry.register(source)

        classified = self.classifier.classify(text)
        summary = self.summarizer.summarize(text)

        item = KnowledgeItem(
            content=summary,
            category=classified["category"],
            source_id=source.source_id,
            confidence=classified["confidence"],
            tags=classified["tags"],
            canonical=canonical,
        )
        return self.store.upsert(item)

    def ingest_chunks(
        self,
        source: KnowledgeSource,
        chunks: Iterable[str],
        canonical: bool = False,
    ) -> List[KnowledgeItem]:
        return [self.ingest_text(source, chunk, canonical=canonical) for chunk in chunks if chunk.strip()]
