from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from orion.artifacts import ArtifactEnvelope

class OperationalMemory:
    FORBIDDEN_FIELDS = {
        "permissions", "policy_override", "bypass_approval", "deploy_token",
        "command_policy", "path_allowlist", "production_approval",
    }

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def record(self, outcome: ArtifactEnvelope) -> None:
        if outcome.artifact_type != "outcome":
            raise ValueError("only_outcome_artifact_can_be_learned")
        payload = outcome.payload
        forbidden = self.FORBIDDEN_FIELDS.intersection(payload)
        if forbidden:
            raise ValueError("forbidden_learning_fields:" + ",".join(sorted(forbidden)))
        if not payload.get("validation_id"):
            raise ValueError("validated_outcome_required")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "artifact_id": outcome.artifact_id,
            "payload_hash": outcome.payload_hash,
            "schema_version": outcome.schema_version,
            "created_at": outcome.created_at,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def find_similar(self, *, root_cause: str = "", affected_files: tuple[str, ...] = ()) -> list[dict[str, Any]]:
        needle = root_cause.lower().strip()
        files = set(affected_files)
        matches = []
        for record in self.read_all():
            payload = record["payload"]
            haystack = json.dumps(payload, ensure_ascii=False).lower()
            score = (2 if needle and needle in haystack else 0)
            score += len(files.intersection(payload.get("affected_files", ())))
            if score:
                matches.append({"score": score, **record})
        return sorted(matches, key=lambda item: item["score"], reverse=True)
