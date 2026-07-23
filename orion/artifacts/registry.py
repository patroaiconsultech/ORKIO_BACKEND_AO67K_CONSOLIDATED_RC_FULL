from __future__ import annotations
from collections.abc import Callable
from typing import Any
from .base import ArtifactEnvelope

Validator = Callable[[dict[str, Any]], None]

class ArtifactRegistry:
    def __init__(self) -> None:
        self._validators: dict[tuple[str, str], Validator] = {}

    def register(self, artifact_type: str, schema_version: str, validator: Validator) -> None:
        key = (artifact_type, schema_version)
        if key in self._validators:
            raise ValueError("artifact_schema_already_registered")
        self._validators[key] = validator

    def supports(self, artifact_type: str, schema_version: str) -> bool:
        return (artifact_type, schema_version) in self._validators

    def validate(self, envelope: ArtifactEnvelope) -> None:
        validator = self._validators.get((envelope.artifact_type, envelope.schema_version))
        if validator is None:
            raise ValueError("unsupported_artifact_schema")
        validator(envelope.payload)
