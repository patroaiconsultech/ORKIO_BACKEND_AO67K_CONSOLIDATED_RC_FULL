from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EvolutionMemory:
    """Append-only JSONL memory. It cannot change governance or permissions."""

    FORBIDDEN_FIELDS = {"permissions", "policy_override", "bypass_approval", "deploy_token"}

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def record(self, outcome: dict[str, Any]) -> None:
        if self.FORBIDDEN_FIELDS.intersection(outcome):
            raise ValueError("forbidden_learning_fields")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(outcome, ensure_ascii=False, sort_keys=True) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [
            json.loads(line)
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
