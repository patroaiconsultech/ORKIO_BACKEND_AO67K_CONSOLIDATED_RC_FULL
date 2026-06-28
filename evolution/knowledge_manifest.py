from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class KnowledgeManifestEntry:
    document_id: str
    title: str
    tags: list[str] = field(default_factory=list)
    source: str = "manual"
    scope: str = "general"
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True
    created_at: str = field(default_factory=_now_utc)
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate_governance(self) -> None:
        if self.proposal_only is not True:
            raise ValueError("Knowledge governance violation: proposal_only must be True")
        if self.write_executed is not False:
            raise ValueError("Knowledge governance violation: write_executed must be False")
        if self.human_approval_required is not True:
            raise ValueError("Knowledge governance violation: human_approval_required must be True")
        if not self.document_id:
            raise ValueError("Knowledge manifest violation: document_id is required")
        if not self.title:
            raise ValueError("Knowledge manifest violation: title is required")

    def to_dict(self) -> dict[str, Any]:
        self.validate_governance()
        return asdict(self)


class KnowledgeManifest:
    def __init__(self) -> None:
        self._entries: dict[str, KnowledgeManifestEntry] = {}

    def register(self, entry: KnowledgeManifestEntry) -> dict[str, Any]:
        entry.validate_governance()
        self._entries[entry.document_id] = entry
        return entry.to_dict()

    def list_entries(self) -> list[dict[str, Any]]:
        return [entry.to_dict() for entry in self._entries.values()]

    def get(self, document_id: str) -> dict[str, Any] | None:
        entry = self._entries.get(document_id)
        return entry.to_dict() if entry else None

    def validate_all(self) -> bool:
        for entry in self._entries.values():
            entry.validate_governance()
        return True
