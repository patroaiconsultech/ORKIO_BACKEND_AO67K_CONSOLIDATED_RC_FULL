from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any
from uuid import uuid4

@dataclass(frozen=True)
class MemorySnapshot:
    snapshot_id: str
    created_at: str
    outcome_count: int
    pattern_count: int
    source_hashes: tuple[str, ...]
    index_version: str
    policy_version: str

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)

def create_snapshot(records: list[dict[str, Any]], patterns: list[Any], *, index_version: str = "1.0", policy_version: str = "1.0") -> MemorySnapshot:
    hashes = tuple(sorted(str(item.get("payload_hash", "")) for item in records if item.get("payload_hash")))
    digest = sha256(json.dumps(hashes).encode("utf-8")).hexdigest()[:12]
    return MemorySnapshot(
        snapshot_id=f"snapshot_{digest}_{uuid4().hex[:8]}",
        created_at=datetime.now(timezone.utc).isoformat(),
        outcome_count=len(records),
        pattern_count=len(patterns),
        source_hashes=hashes,
        index_version=index_version,
        policy_version=policy_version,
    )
