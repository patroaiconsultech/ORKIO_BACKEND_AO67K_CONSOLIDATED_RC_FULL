from __future__ import annotations

import os
from typing import Any


EVOLUTION_INTELLIGENCE_VERSION = "ORKIO-EVOLUTION-INTELLIGENCE-R1.1"


class EvolutionGovernanceError(RuntimeError):
    pass


def _flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def load_evolution_governance_config() -> dict[str, Any]:
    return {
        "version": EVOLUTION_INTELLIGENCE_VERSION,
        "environment": str(os.getenv("APP_ENV") or "unknown").strip().lower(),
        "center_enabled": _flag("EVOLUTION_CENTER_ENABLED", True),
        "kpi_collection_enabled": _flag("EVOLUTION_KPI_COLLECTION_ENABLED", True),
        "config_write_enabled": _flag("EVOLUTION_CONFIG_WRITE_ENABLED", False),
        "health_snapshot_write_enabled": _flag(
            "EVOLUTION_HEALTH_SNAPSHOT_WRITE_ENABLED",
            False,
        ),
        "proposal_generation_enabled": _flag(
            "EVOLUTION_PROPOSAL_GENERATION_ENABLED",
            False,
        ),
        "proposal_only": _flag("EVOLUTION_PROPOSAL_ONLY", True),
        "diff_preview_enabled": _flag("EVOLUTION_DIFF_PREVIEW_ENABLED", True),
        "write_enabled": _flag("EVOLUTION_WRITE_ENABLED", False),
        "auto_apply_enabled": _flag("EVOLUTION_AUTO_APPLY_ENABLED", False),
        "human_approval_required": _flag(
            "EVOLUTION_HUMAN_APPROVAL_REQUIRED",
            True,
        ),
        "rollback_required": _flag("EVOLUTION_ROLLBACK_REQUIRED", True),
    }


def validate_evolution_governance_config(
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cfg = dict(config or load_evolution_governance_config())
    violations: list[str] = []
    if cfg["auto_apply_enabled"] and not cfg["write_enabled"]:
        violations.append("auto_apply_requires_write_enabled")
    if cfg["auto_apply_enabled"]:
        violations.append("auto_apply_not_allowed_in_foundation_r1")
    if cfg["write_enabled"]:
        violations.append("code_write_not_allowed_in_foundation_r1")
    if cfg["environment"] in {"production", "prod"}:
        if not cfg["human_approval_required"]:
            violations.append("production_requires_human_approval")
        if not cfg["proposal_only"]:
            violations.append("production_requires_proposal_only")
        if not cfg["rollback_required"]:
            violations.append("production_requires_rollback")
    if violations:
        raise EvolutionGovernanceError(
            "EVOLUTION_GOVERNANCE_INVALID:" + ",".join(sorted(set(violations)))
        )
    cfg["valid"] = True
    cfg["violations"] = []
    return cfg
