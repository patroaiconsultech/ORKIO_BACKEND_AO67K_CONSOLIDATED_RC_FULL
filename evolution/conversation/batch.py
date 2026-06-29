from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from evolution.conversation.distiller import ConversationDistiller
from evolution.conversation.idempotency import make_idempotency_key


@dataclass
class BatchDistillationItem:
    idempotency_key: str
    conversation: str
    status: str
    result: object | None = None


@dataclass
class BatchDistillationReport:
    processed: int = 0
    skipped: int = 0
    duplicates: int = 0
    results: list[BatchDistillationItem] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "processed": self.processed,
            "skipped": self.skipped,
            "duplicates": self.duplicates,
            "results": [
                {
                    "idempotency_key": item.idempotency_key,
                    "conversation": item.conversation,
                    "status": item.status,
                    "result": item.result,
                }
                for item in self.results
            ],
        }


class ConversationBatchProcessor:
    """Deterministic batch processor with in-memory idempotency registry.

    This class is intentionally storage-agnostic. A future OEP can replace the
    in-memory key set with a persistent repository without changing callers.
    """

    def __init__(self, distiller: ConversationDistiller | None = None) -> None:
        self._distiller = distiller or ConversationDistiller()
        self._seen_keys: set[str] = set()

    def has_seen(self, conversation: str) -> bool:
        return make_idempotency_key(conversation) in self._seen_keys

    def reset(self) -> None:
        self._seen_keys.clear()

    def distill_batch(self, conversations: Iterable[str]) -> BatchDistillationReport:
        report = BatchDistillationReport()

        for raw in conversations:
            conversation = raw or ""
            key = make_idempotency_key(conversation)

            if not conversation.strip():
                report.skipped += 1
                report.results.append(
                    BatchDistillationItem(
                        idempotency_key=key,
                        conversation=conversation,
                        status="skipped",
                        result=None,
                    )
                )
                continue

            if key in self._seen_keys:
                report.duplicates += 1
                report.skipped += 1
                report.results.append(
                    BatchDistillationItem(
                        idempotency_key=key,
                        conversation=conversation,
                        status="duplicate",
                        result=None,
                    )
                )
                continue

            result = self._distiller.distill(conversation)
            self._seen_keys.add(key)
            report.processed += 1
            report.results.append(
                BatchDistillationItem(
                    idempotency_key=key,
                    conversation=conversation,
                    status="processed",
                    result=result,
                )
            )

        return report
