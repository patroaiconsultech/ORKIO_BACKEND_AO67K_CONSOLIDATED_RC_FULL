from __future__ import annotations

"""Single authorization gate for governed ORKIO mutations.

This module does not execute mutations. It only validates whether a previously
approved proposal may authorize a specific action at the current time.

The first release intentionally reuses EvolutionProposal instead of introducing
a new approval table. ``approval_id`` is therefore an alias for ``proposal_id``.
A future migration may replace this adapter with immutable scoped approvals
without changing callers.
"""

from dataclasses import asdict, dataclass
import os
import time
from typing import Any, Mapping, Optional


MUTATION_AUTHORITY_VERSION = "EGA005_MUTATION_AUTHORITY_V1"

_MUTATING_ACTIONS = {
    "db_schema_direct",
    "create_branch",
    "write_file",
    "create_commit",
    "open_pr",
    "merge_pr",
    "deploy",
    "rollback",
}

_ACTION_ENV = {
    "db_schema_direct": "EVOLUTION_ALLOW_DIRECT_SCHEMA",
    "create_branch": "EVOLUTION_ALLOW_CREATE_BRANCH",
    "write_file": "EVOLUTION_ALLOW_WRITE_FILE",
    "create_commit": "EVOLUTION_ALLOW_CREATE_COMMIT",
    "open_pr": "EVOLUTION_ALLOW_OPEN_PR",
    "merge_pr": "EVOLUTION_ALLOW_MERGE_PR",
    "deploy": "EVOLUTION_ALLOW_DEPLOY",
    "rollback": "EVOLUTION_ALLOW_ROLLBACK",
}


def _env_bool(name: str, default: bool = False) -> bool:
    raw = str(os.getenv(name, "true" if default else "false") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(str(os.getenv(name, str(default)) or default).strip())
    except Exception:
        return int(default)


def mutation_authority_required() -> bool:
    # SEC-001: fail closed. A missing variable must never silently restore
    # observe-only mutation authorization.
    return _env_bool("EVOLUTION_MUTATION_AUTHORITY_REQUIRED", True)


@dataclass(frozen=True)
class MutationDecision:
    allowed: bool
    reason: str
    action: str
    proposal_id: str = ""
    approval_id: str = ""
    actor: str = ""
    target: str = ""
    approval_age_seconds: Optional[int] = None
    approval_ttl_seconds: Optional[int] = None
    authority_version: str = MUTATION_AUTHORITY_VERSION
    legacy_mode: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _snapshot_value(snapshot: Mapping[str, Any], key: str, default: Any = None) -> Any:
    try:
        return snapshot.get(key, default)
    except Exception:
        return default


def authorize_proposal_snapshot(
    proposal: Mapping[str, Any],
    *,
    action: str,
    actor: str,
    target: str = "",
    approval_id: Optional[str] = None,
    require_dry_run: bool = False,
    now: Optional[int] = None,
) -> MutationDecision:
    action = str(action or "").strip().lower()
    actor = str(actor or "").strip()
    target = str(target or "").strip()
    proposal_id = str(_snapshot_value(proposal, "id", "") or "").strip()
    supplied_approval_id = str(approval_id or proposal_id or "").strip()

    if action not in _MUTATING_ACTIONS:
        return MutationDecision(
            False, "unknown_mutation_action", action,
            proposal_id=proposal_id, approval_id=supplied_approval_id,
            actor=actor, target=target,
        )

    if not mutation_authority_required():
        return MutationDecision(
            True, "mutation_authority_observe_only", action,
            proposal_id=proposal_id, approval_id=supplied_approval_id,
            actor=actor, target=target, legacy_mode=True,
        )

    action_env = _ACTION_ENV[action]
    if not _env_bool(action_env, False):
        return MutationDecision(
            False, f"action_disabled:{action_env}", action,
            proposal_id=proposal_id, approval_id=supplied_approval_id,
            actor=actor, target=target,
        )

    if not proposal_id:
        return MutationDecision(False, "proposal_id_required", action, actor=actor, target=target)

    if supplied_approval_id != proposal_id:
        return MutationDecision(
            False, "approval_id_must_match_proposal_id_v1", action,
            proposal_id=proposal_id, approval_id=supplied_approval_id,
            actor=actor, target=target,
        )

    status = str(_snapshot_value(proposal, "status", "") or "").strip().lower()
    allowed_statuses = {"approved", "executed", "failed", "rolled_back"} if action == "rollback" else {"approved"}
    if status not in allowed_statuses:
        return MutationDecision(
            False, f"proposal_status_not_authorized:{status or 'empty'}", action,
            proposal_id=proposal_id, approval_id=supplied_approval_id,
            actor=actor, target=target,
        )

    approved_by = str(_snapshot_value(proposal, "approved_by", "") or "").strip()
    approved_at = int(_snapshot_value(proposal, "approved_at", 0) or 0)
    if not approved_by or approved_at <= 0:
        return MutationDecision(
            False, "persisted_human_approval_required", action,
            proposal_id=proposal_id, approval_id=supplied_approval_id,
            actor=actor, target=target,
        )

    if not actor:
        return MutationDecision(
            False, "execution_actor_required", action,
            proposal_id=proposal_id, approval_id=supplied_approval_id,
            target=target,
        )

    now = int(now or time.time())
    ttl = max(60, _env_int("EVOLUTION_APPROVAL_TTL_SECONDS", 3600))
    age = max(0, now - approved_at)
    if action != "rollback" and age > ttl:
        return MutationDecision(
            False, "approval_expired", action,
            proposal_id=proposal_id, approval_id=supplied_approval_id,
            actor=actor, target=target,
            approval_age_seconds=age, approval_ttl_seconds=ttl,
        )

    if require_dry_run:
        execution_status = str(
            _snapshot_value(proposal, "execution_status", "")
            or _snapshot_value(proposal, "last_execution_status", "")
            or ""
        ).strip().lower()
        if execution_status != "dry_run_completed":
            return MutationDecision(
                False, "dry_run_completed_required", action,
                proposal_id=proposal_id, approval_id=supplied_approval_id,
                actor=actor, target=target,
                approval_age_seconds=age, approval_ttl_seconds=ttl,
            )

    return MutationDecision(
        True, "governed_mutation_authorized", action,
        proposal_id=proposal_id, approval_id=supplied_approval_id,
        actor=actor, target=target,
        approval_age_seconds=age, approval_ttl_seconds=ttl,
    )


def authorize_database_proposal(
    db: Any,
    *,
    proposal_id: str,
    action: str,
    actor: str,
    target: str = "",
    approval_id: Optional[str] = None,
    require_dry_run: bool = False,
) -> MutationDecision:
    proposal_id = str(proposal_id or "").strip()
    if not proposal_id:
        return MutationDecision(False, "proposal_id_required", str(action or ""), actor=actor, target=target)

    try:
        from app.models import EvolutionProposal
        row = db.query(EvolutionProposal).filter(EvolutionProposal.id == proposal_id).first()
    except Exception as exc:
        return MutationDecision(
            False, f"proposal_lookup_failed:{type(exc).__name__}",
            str(action or ""), proposal_id=proposal_id,
            approval_id=str(approval_id or ""), actor=actor, target=target,
        )

    if row is None:
        return MutationDecision(
            False, "proposal_not_found", str(action or ""),
            proposal_id=proposal_id, approval_id=str(approval_id or ""),
            actor=actor, target=target,
        )

    snapshot = {
        "id": getattr(row, "id", ""),
        "status": getattr(row, "status", ""),
        "approved_by": getattr(row, "approved_by", ""),
        "approved_at": getattr(row, "approved_at", 0),
        "last_execution_status": getattr(row, "last_execution_status", ""),
    }
    return authorize_proposal_snapshot(
        snapshot,
        action=action,
        actor=actor,
        target=target,
        approval_id=approval_id,
        require_dry_run=require_dry_run,
    )
