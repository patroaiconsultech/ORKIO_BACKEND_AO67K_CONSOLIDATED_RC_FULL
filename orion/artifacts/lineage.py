from __future__ import annotations
from .base import ArtifactEnvelope

REQUIRED_PARENT_TYPES = {
    "diagnosis": {"evidence"},
    "proposal": {"diagnosis"},
    "governance": {"proposal"},
    "execution": {"governance"},
    "validation": {"execution"},
    "outcome": {"validation"},
    "agent_result": {"agent_task"},
}

class ArtifactLineage:
    def validate(self, child: ArtifactEnvelope, parents: list[ArtifactEnvelope]) -> None:
        declared = set(child.parent_artifact_ids)
        actual = {p.artifact_id for p in parents}
        if declared != actual:
            raise ValueError("artifact_lineage_reference_mismatch")
        required = REQUIRED_PARENT_TYPES.get(child.artifact_type, set())
        present = {p.artifact_type for p in parents}
        if not required.issubset(present):
            raise ValueError("artifact_lineage_incomplete")
