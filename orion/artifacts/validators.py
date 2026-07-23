from __future__ import annotations
from typing import Any
from .registry import ArtifactRegistry

def require(*fields: str):
    def validate(payload: dict[str, Any]) -> None:
        missing = [f for f in fields if payload.get(f) in (None, "", [], (), {})]
        if missing:
            raise ValueError("missing_artifact_fields:" + ",".join(missing))
    return validate

def validate_proposal(payload: dict[str, Any]) -> None:
    require("objective","diagnosis_id","evidence_ids","affected_files","diff_preview","risk","rollback","tests")(payload)
    if payload.get("proposal_only") is not True:
        raise ValueError("proposal_only_required")
    if payload.get("requires_human_approval") is not True:
        raise ValueError("human_approval_required")

def validate_governance(payload: dict[str, Any]) -> None:
    require("proposal_id","decision","reasons","policy_version")(payload)
    allowed = {"blocked","approval_required","approved_for_simulation","approved_for_sandbox","rejected"}
    if payload["decision"] not in allowed:
        raise ValueError("invalid_governance_decision")
    if payload.get("target_environment") == "production":
        raise ValueError("production_approval_forbidden")

def validate_agent_task(payload: dict[str, Any]) -> None:
    require("requested_by","assigned_agent","specialty","objective","input_artifact_ids","status")(payload)

def validate_agent_result(payload: dict[str, Any]) -> None:
    require("task_id","agent_id","specialty","summary","cited_agent")(payload)
    if payload["cited_agent"] != payload["agent_id"]:
        raise ValueError("agent_citation_mismatch")

def default_registry() -> ArtifactRegistry:
    registry = ArtifactRegistry()
    registry.register("evidence","1.0",require("source_type","source_ref","fact"))
    registry.register("diagnosis","1.0",require("primary_root_cause","evidence_ids"))
    registry.register("proposal","1.0",validate_proposal)
    registry.register("governance","1.0",validate_governance)
    registry.register("agent_task","1.0",validate_agent_task)
    registry.register("agent_result","1.0",validate_agent_result)
    registry.register("execution","1.0",require("proposal_id","governance_id","workspace_id"))
    registry.register("validation","1.0",require("execution_id","status","checks"))
    registry.register("outcome","1.0",require("cycle_id","proposal_id","execution_id","validation_id","result"))
    registry.register("memory_snapshot","1.0",require("snapshot_id","outcome_count","pattern_count","index_version","policy_version"))
    return registry
