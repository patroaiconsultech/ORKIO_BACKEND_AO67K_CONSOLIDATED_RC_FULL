from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any


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
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate_governance(self) -> None:
        if self.proposal_only is not True:
            raise ValueError("KnowledgeManifestEntry requires proposal_only=True")
        if self.write_executed is not False:
            raise ValueError("KnowledgeManifestEntry requires write_executed=False")
        if self.human_approval_required is not True:
            raise ValueError("KnowledgeManifestEntry requires human_approval_required=True")

    def to_dict(self) -> dict[str, Any]:
        self.validate_governance()
        return asdict(self)


class KnowledgeManifest:
    def __init__(self) -> None:
        self._entries: dict[str, KnowledgeManifestEntry] = {}

    def register(self, document: dict[str, Any]) -> dict[str, Any]:
        document_id = str(document.get("document_id") or document.get("id") or "").strip()
        if not document_id:
            raise ValueError("document_id is required to register knowledge manifest entry")

        entry = KnowledgeManifestEntry(
            document_id=document_id,
            title=str(document.get("title") or ""),
            tags=list(document.get("tags") or []),
            source=str(document.get("source") or "manual"),
            scope=str(document.get("scope") or "general"),
            proposal_only=bool(document.get("proposal_only", True)),
            write_executed=bool(document.get("write_executed", False)),
            human_approval_required=bool(document.get("human_approval_required", True)),
            created_at=str(document.get("created_at") or datetime.now(timezone.utc).isoformat()),
            metadata=dict(document.get("metadata") or {}),
        )
        entry.validate_governance()
        self._entries[document_id] = entry
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
