from __future__ import annotations
from typing import Any
from .base import ArtifactEnvelope
from .types import payload_of

def envelope_for(
    artifact_type: str,
    payload: Any,
    *,
    cycle_id: str,
    correlation_id: str,
    producer: str,
    parents: tuple[str, ...] = (),
    metadata: dict[str, Any] | None = None,
) -> ArtifactEnvelope:
    data = payload_of(payload) if not isinstance(payload, dict) else dict(payload)
    return ArtifactEnvelope(
        artifact_type=artifact_type,
        schema_version="1.0",
        cycle_id=cycle_id,
        correlation_id=correlation_id,
        producer=producer,
        payload=data,
        parent_artifact_ids=parents,
        metadata=metadata or {},
    )
