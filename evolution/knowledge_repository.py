from __future__ import annotations

from typing import Protocol, Iterable, Any


class KnowledgeRepository(Protocol):
    def add(self, title: str, content: str, tags: list[str] | None = None) -> dict:
        ...

    def search(self, query: str) -> list[dict]:
        ...

    def list_all(self) -> list[dict]:
        ...


class InMemoryKnowledgeRepository:
    """Repository adapter over KnowledgeVault.

    This keeps OEP-003.1 backend-only and non-invasive.
    """

    def __init__(self, vault: Any) -> None:
        self._vault = vault

    def add(self, title: str, content: str, tags: list[str] | None = None) -> dict:
        return self._vault.add(title=title, content=content, tags=tags)

    def search(self, query: str) -> list[dict]:
        return self._vault.search(query=query)

    def list_all(self) -> list[dict]:
        items = getattr(self._vault, "_items", [])
        result: list[dict] = []
        for item in items:
            if hasattr(item, "__dataclass_fields__"):
                from dataclasses import asdict
                result.append(asdict(item))
            elif isinstance(item, dict):
                result.append(dict(item))
        return result
