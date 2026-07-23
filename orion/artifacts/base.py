from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any
from uuid import uuid4

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)

@dataclass(frozen=True)
class ArtifactEnvelope:
    artifact_type: str
    schema_version: str
    cycle_id: str
    correlation_id: str
    producer: str
    payload: dict[str, Any]
    parent_artifact_ids: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    artifact_id: str = field(default_factory=lambda: f"artifact_{uuid4().hex[:20]}")
    created_at: str = field(default_factory=utc_now)
    payload_hash: str = ""

    def __post_init__(self) -> None:
        if not self.artifact_type or not self.schema_version:
            raise ValueError("artifact_type_and_schema_version_required")
        if not self.cycle_id or not self.correlation_id or not self.producer:
            raise ValueError("artifact_context_required")
        expected = sha256(canonical_json(self.payload).encode("utf-8")).hexdigest()
        if self.payload_hash and self.payload_hash != expected:
            raise ValueError("artifact_payload_hash_mismatch")
        object.__setattr__(self, "payload_hash", expected)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["parent_artifact_ids"] = list(self.parent_artifact_ids)
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "ArtifactEnvelope":
        data = dict(value)
        data["parent_artifact_ids"] = tuple(data.get("parent_artifact_ids", ()))
        return cls(**data)
