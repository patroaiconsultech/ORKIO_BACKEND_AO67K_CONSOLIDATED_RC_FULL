from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Optional

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.evolution.intelligence.diagnostics import build_diagnostic_preview
from app.evolution.intelligence.kpi_registry import (
    KPI_COLLECTOR_VERSION,
    KPI_SOURCE_VERSION,
    get_kpi_definition,
    registry_payload,
)
from app.evolution.intelligence.prioritization import build_priority_preview
from app.evolution.intelligence.scoring import build_project_health_preview
from app.services.evolution_signal_service import build_current_snapshot


OBJECTIVES_TABLE = "evolution_objectives"
TARGETS_TABLE = "evolution_kpi_targets"
TARGET_VERSIONS_TABLE = "evolution_kpi_target_versions"
HEALTH_SNAPSHOTS_TABLE = "evolution_health_snapshots"
HEALTH_PROVENANCE_TABLE = "evolution_health_snapshot_provenance"
HEALTH_EVENTS_TABLE = "evolution_health_snapshot_events"


def _tables(db: Session) -> set[str]:
    return set(inspect(db.connection()).get_table_names())


def foundation_schema_status(db: Session) -> dict[str, Any]:
    names = _tables(db)
    required = {
        OBJECTIVES_TABLE,
        TARGETS_TABLE,
        TARGET_VERSIONS_TABLE,
        HEALTH_SNAPSHOTS_TABLE,
        HEALTH_PROVENANCE_TABLE,
        HEALTH_EVENTS_TABLE,
    }
    missing = sorted(required - names)
    return {
        "available": not missing,
        "missing_tables": missing,
        "required_tables": sorted(required),
    }


def list_objectives(
    db: Session,
    *,
    org_slug: str,
    status: Optional[str] = None,
) -> list[dict[str, Any]]:
    if OBJECTIVES_TABLE not in _tables(db):
        return []
    clauses = ["org_slug = :org_slug"]
    params: dict[str, Any] = {"org_slug": org_slug}
    if status:
        clauses.append("status = :status")
        params["status"] = status
    rows = db.execute(
        text(
            f"""
            SELECT id, org_slug, name, description, category, priority, status,
                   starts_at, ends_at, owner_ref, success_definition,
                   proposal_policy, human_approval_required, version,
                   created_at, updated_at
            FROM {OBJECTIVES_TABLE}
            WHERE {' AND '.join(clauses)}
            ORDER BY priority DESC, updated_at DESC
            """
        ),
        params,
    ).mappings().all()
    return [dict(row) for row in rows]


def count_active_objectives(db: Session, *, org_slug: str) -> int:
    if OBJECTIVES_TABLE not in _tables(db):
        return 0
    return int(
        db.execute(
            text(
                f"""
                SELECT COUNT(*)
                FROM {OBJECTIVES_TABLE}
                WHERE org_slug = :org_slug AND status = 'active'
                """
            ),
            {"org_slug": org_slug},
        ).scalar_one()
        or 0
    )


def get_objective(
    db: Session,
    *,
    org_slug: str,
    objective_id: str,
) -> Optional[dict[str, Any]]:
    if OBJECTIVES_TABLE not in _tables(db):
        return None
    row = db.execute(
        text(
            f"""
            SELECT id, org_slug, name, description, category, priority, status,
                   starts_at, ends_at, owner_ref, success_definition,
                   proposal_policy, human_approval_required, version,
                   created_at, updated_at
            FROM {OBJECTIVES_TABLE}
            WHERE id = :objective_id AND org_slug = :org_slug
            LIMIT 1
            """
        ),
        {"objective_id": objective_id, "org_slug": org_slug},
    ).mappings().first()
    return dict(row) if row else None


def create_objective(
    db: Session,
    *,
    org_slug: str,
    objective_id: str,
    payload: Mapping[str, Any],
    actor_ref: str,
    now_ts: int,
) -> dict[str, Any]:
    if OBJECTIVES_TABLE not in _tables(db):
        raise RuntimeError("EVOLUTION_INTELLIGENCE_SCHEMA_UNAVAILABLE")
    if str(payload.get("status") or "draft") == "active":
        if count_active_objectives(db, org_slug=org_slug) >= 5:
            raise ValueError("ACTIVE_OBJECTIVE_LIMIT_REACHED")
    db.execute(
        text(
            f"""
            INSERT INTO {OBJECTIVES_TABLE} (
                id, org_slug, name, description, category, priority, status,
                starts_at, ends_at, owner_ref, success_definition,
                proposal_policy, human_approval_required, version,
                created_by, updated_by, created_at, updated_at
            ) VALUES (
                :id, :org_slug, :name, :description, :category, :priority, :status,
                :starts_at, :ends_at, :owner_ref, :success_definition,
                'proposal_only', TRUE, 1,
                :actor_ref, :actor_ref, :created_at, :updated_at
            )
            """
        ),
        {
            "id": objective_id,
            "org_slug": org_slug,
            "name": payload["name"],
            "description": payload["description"],
            "category": payload["category"],
            "priority": payload["priority"],
            "status": payload["status"],
            "starts_at": payload.get("starts_at"),
            "ends_at": payload.get("ends_at"),
            "owner_ref": payload["owner_ref"],
            "success_definition": payload["success_definition"],
            "actor_ref": actor_ref,
            "created_at": now_ts,
            "updated_at": now_ts,
        },
    )
    result = get_objective(db, org_slug=org_slug, objective_id=objective_id)
    if result is None:
        raise RuntimeError("EVOLUTION_OBJECTIVE_CREATE_FAILED")
    return result


def update_objective(
    db: Session,
    *,
    org_slug: str,
    objective_id: str,
    payload: Mapping[str, Any],
    actor_ref: str,
    now_ts: int,
) -> Optional[dict[str, Any]]:
    current = get_objective(db, org_slug=org_slug, objective_id=objective_id)
    if current is None:
        return None
    allowed = {
        "name",
        "description",
        "category",
        "priority",
        "status",
        "starts_at",
        "ends_at",
        "owner_ref",
        "success_definition",
    }
    values = {key: value for key, value in payload.items() if key in allowed and value is not None}
    if not values:
        return current
    if values.get("status") == "active" and current.get("status") != "active":
        if count_active_objectives(db, org_slug=org_slug) >= 5:
            raise ValueError("ACTIVE_OBJECTIVE_LIMIT_REACHED")
    assignments = [f"{key} = :{key}" for key in values]
    params = {
        **values,
        "org_slug": org_slug,
        "objective_id": objective_id,
        "updated_by": actor_ref,
        "updated_at": now_ts,
    }
    assignments.extend(
        ["version = version + 1", "updated_by = :updated_by", "updated_at = :updated_at"]
    )
    db.execute(
        text(
            f"""
            UPDATE {OBJECTIVES_TABLE}
            SET {', '.join(assignments)}
            WHERE id = :objective_id AND org_slug = :org_slug
            """
        ),
        params,
    )
    return get_objective(db, org_slug=org_slug, objective_id=objective_id)


def list_target_overrides(
    db: Session,
    *,
    org_slug: str,
    objective_id: Optional[str] = None,
) -> list[dict[str, Any]]:
    if TARGETS_TABLE not in _tables(db):
        return []
    clauses = ["org_slug = :org_slug"]
    params: dict[str, Any] = {"org_slug": org_slug}
    if objective_id:
        clauses.append("objective_id = :objective_id")
        params["objective_id"] = objective_id
    else:
        clauses.append("objective_id IS NULL")
    rows = db.execute(
        text(
            f"""
            SELECT id, org_slug, objective_id, scope_key, kpi_code, target_value,
                   warning_threshold, critical_threshold, weight,
                   minimum_sample_size, enabled, proposal_enabled,
                   auto_apply_enabled, version, starts_at, ends_at,
                   created_at, updated_at
            FROM {TARGETS_TABLE}
            WHERE {' AND '.join(clauses)}
            ORDER BY kpi_code ASC
            """
        ),
        params,
    ).mappings().all()
    return [dict(row) for row in rows]


def target_override_map(
    db: Session,
    *,
    org_slug: str,
    objective_id: Optional[str],
) -> dict[str, dict[str, Any]]:
    defaults = {
        row["kpi_code"]: row
        for row in list_target_overrides(db, org_slug=org_slug, objective_id=None)
    }
    if objective_id:
        defaults.update(
            {
                row["kpi_code"]: row
                for row in list_target_overrides(
                    db,
                    org_slug=org_slug,
                    objective_id=objective_id,
                )
            }
        )
    return defaults


def list_target_history(
    db: Session,
    *,
    org_slug: str,
    objective_id: Optional[str] = None,
    kpi_code: Optional[str] = None,
    limit: int = 200,
) -> list[dict[str, Any]]:
    if TARGET_VERSIONS_TABLE not in _tables(db):
        return []
    clauses = ["org_slug = :org_slug"]
    params: dict[str, Any] = {"org_slug": org_slug, "limit": limit}
    if objective_id:
        clauses.append("objective_id = :objective_id")
        params["objective_id"] = objective_id
    elif objective_id is None:
        # None means all scopes for history; callers can filter with kpi_code.
        pass
    if kpi_code:
        clauses.append("kpi_code = :kpi_code")
        params["kpi_code"] = kpi_code
    rows = db.execute(
        text(
            f"""
            SELECT id, org_slug, target_id, objective_id, scope_key, kpi_code,
                   version, target_value, warning_threshold, critical_threshold,
                   weight, minimum_sample_size, enabled, proposal_enabled,
                   auto_apply_enabled, effective_from, effective_to,
                   changed_by, change_reason, approval_id, created_at
            FROM {TARGET_VERSIONS_TABLE}
            WHERE {' AND '.join(clauses)}
            ORDER BY effective_from DESC, version DESC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()
    return [dict(row) for row in rows]


def upsert_target(
    db: Session,
    *,
    org_slug: str,
    target_id: str,
    payload: Mapping[str, Any],
    actor_ref: str,
    now_ts: int,
    version_id: Optional[str] = None,
) -> dict[str, Any]:
    tables = _tables(db)
    if TARGETS_TABLE not in tables or TARGET_VERSIONS_TABLE not in tables:
        raise RuntimeError("EVOLUTION_INTELLIGENCE_SCHEMA_UNAVAILABLE")
    objective_id = payload.get("objective_id")
    if objective_id and get_objective(
        db,
        org_slug=org_slug,
        objective_id=str(objective_id),
    ) is None:
        raise LookupError("OBJECTIVE_NOT_FOUND")
    if get_kpi_definition(str(payload["kpi_code"])) is None:
        raise LookupError("KPI_NOT_FOUND")

    change_reason = str(payload.get("change_reason") or "").strip()
    approval_id = str(payload.get("approval_id") or "").strip()
    if len(change_reason) < 8:
        raise ValueError("TARGET_CHANGE_REASON_REQUIRED")
    if not approval_id:
        raise ValueError("TARGET_APPROVAL_ID_REQUIRED")

    scope_key = str(objective_id or "__global__")
    existing = db.execute(
        text(
            f"""
            SELECT id, version
            FROM {TARGETS_TABLE}
            WHERE org_slug = :org_slug
              AND kpi_code = :kpi_code
              AND scope_key = :scope_key
            LIMIT 1
            """
        ),
        {
            "org_slug": org_slug,
            "kpi_code": payload["kpi_code"],
            "scope_key": scope_key,
        },
    ).mappings().first()

    current_target_id = str(existing["id"]) if existing else target_id
    next_version = int(existing["version"] or 0) + 1 if existing else 1
    history_id = (
        version_id
        or f"etgv_{current_target_id[:18]}_{next_version}_{now_ts}"[:96]
    )

    params = {
        "id": current_target_id,
        "org_slug": org_slug,
        "objective_id": objective_id,
        "scope_key": scope_key,
        "kpi_code": payload["kpi_code"],
        "target_value": payload["target_value"],
        "warning_threshold": payload["warning_threshold"],
        "critical_threshold": payload["critical_threshold"],
        "weight": payload["weight"],
        "minimum_sample_size": payload["minimum_sample_size"],
        "enabled": bool(payload["enabled"]),
        "proposal_enabled": bool(payload["proposal_enabled"]),
        "auto_apply_enabled": False,
        "actor_ref": actor_ref,
        "now_ts": now_ts,
        "version": next_version,
        "history_id": history_id,
        "change_reason": change_reason,
        "approval_id": approval_id,
    }

    if existing:
        db.execute(
            text(
                f"""
                UPDATE {TARGET_VERSIONS_TABLE}
                SET effective_to = :now_ts
                WHERE target_id = :id
                  AND org_slug = :org_slug
                  AND version = :previous_version
                  AND effective_to IS NULL
                """
            ),
            {
                "id": current_target_id,
                "org_slug": org_slug,
                "previous_version": next_version - 1,
                "now_ts": now_ts,
            },
        )
        db.execute(
            text(
                f"""
                UPDATE {TARGETS_TABLE}
                SET target_value=:target_value,
                    warning_threshold=:warning_threshold,
                    critical_threshold=:critical_threshold,
                    weight=:weight,
                    minimum_sample_size=:minimum_sample_size,
                    enabled=:enabled,
                    proposal_enabled=:proposal_enabled,
                    auto_apply_enabled=FALSE,
                    version=:version,
                    updated_by=:actor_ref,
                    updated_at=:now_ts
                WHERE id=:id AND org_slug=:org_slug
                """
            ),
            params,
        )
    else:
        db.execute(
            text(
                f"""
                INSERT INTO {TARGETS_TABLE} (
                    id, org_slug, objective_id, scope_key, kpi_code, target_value,
                    warning_threshold, critical_threshold, weight,
                    minimum_sample_size, enabled, proposal_enabled,
                    auto_apply_enabled, version, starts_at, ends_at,
                    created_by, updated_by, created_at, updated_at
                ) VALUES (
                    :id, :org_slug, :objective_id, :scope_key, :kpi_code, :target_value,
                    :warning_threshold, :critical_threshold, :weight,
                    :minimum_sample_size, :enabled, :proposal_enabled,
                    FALSE, :version, NULL, NULL,
                    :actor_ref, :actor_ref, :now_ts, :now_ts
                )
                """
            ),
            params,
        )

    db.execute(
        text(
            f"""
            INSERT INTO {TARGET_VERSIONS_TABLE} (
                id, org_slug, target_id, objective_id, scope_key, kpi_code,
                version, target_value, warning_threshold, critical_threshold,
                weight, minimum_sample_size, enabled, proposal_enabled,
                auto_apply_enabled, effective_from, effective_to,
                changed_by, change_reason, approval_id, created_at
            ) VALUES (
                :history_id, :org_slug, :id, :objective_id, :scope_key, :kpi_code,
                :version, :target_value, :warning_threshold, :critical_threshold,
                :weight, :minimum_sample_size, :enabled, :proposal_enabled,
                FALSE, :now_ts, NULL,
                :actor_ref, :change_reason, :approval_id, :now_ts
            )
            """
        ),
        params,
    )

    row = db.execute(
        text(
            f"""
            SELECT id, org_slug, objective_id, scope_key, kpi_code, target_value,
                   warning_threshold, critical_threshold, weight,
                   minimum_sample_size, enabled, proposal_enabled,
                   auto_apply_enabled, version, starts_at, ends_at,
                   created_at, updated_at
            FROM {TARGETS_TABLE}
            WHERE id=:id AND org_slug=:org_slug
            """
        ),
        {"id": current_target_id, "org_slug": org_slug},
    ).mappings().one()
    result = dict(row)
    result.update(
        {
            "history_id": history_id,
            "effective_from": now_ts,
            "effective_to": None,
            "changed_by": actor_ref,
            "change_reason": change_reason,
            "approval_id": approval_id,
        }
    )
    return result


def build_inventory(
    db: Session,
    *,
    org_slug: str,
    now_ts: int,
    objective_id: Optional[str] = None,
) -> dict[str, Any]:
    current = build_current_snapshot(db, org_slug=org_slug, now_ts=now_ts)
    registry = registry_payload()
    targets = sorted(
        target_override_map(
            db,
            org_slug=org_slug,
            objective_id=objective_id,
        ).values(),
        key=lambda row: str(row.get("kpi_code") or ""),
    )
    current_codes = {str(metric.get("key") or "") for metric in current.get("metrics") or []}
    registry_codes = {definition["code"] for definition in registry["definitions"]}
    return {
        **registry,
        "org_slug": org_slug,
        "targets": targets,
        "current_metric_codes": sorted(current_codes),
        "registry_without_current_signal": sorted(registry_codes - current_codes),
        "unregistered_current_signals": sorted(current_codes - registry_codes),
        "schema": foundation_schema_status(db),
        "write_executed": False,
    }


def _window_start_for(window: str, now_ts: int) -> int:
    normalized = str(window or "").strip().lower()
    if "90d" in normalized:
        return now_ts - 90 * 86_400
    if "30d" in normalized:
        return now_ts - 30 * 86_400
    if "7d" in normalized:
        return now_ts - 7 * 86_400
    if "24h" in normalized:
        return now_ts - 86_400
    return now_ts


def _health_provenance(
    health: Mapping[str, Any],
    *,
    release_identity: Optional[Mapping[str, Any]],
) -> dict[str, Any]:
    generated_at = int(health.get("generated_at") or 0)
    release = dict(release_identity or {})
    items: list[dict[str, Any]] = []
    window_starts: list[int] = []
    sample_size = 0
    for item in health.get("kpis") or []:
        code = str(item.get("code") or "")
        definition = get_kpi_definition(code)
        time_window = str(
            item.get("time_window")
            or (definition.window if definition is not None else "current")
        )
        window_start = _window_start_for(time_window, generated_at)
        window_starts.append(window_start)
        current_sample = max(0, int(item.get("sample_size") or 0))
        sample_size += current_sample
        items.append(
            {
                "kpi_code": code,
                "collector": (
                    definition.collector if definition is not None else "unknown"
                ),
                "collector_version": str(
                    item.get("collector_version")
                    or (
                        definition.collector_version
                        if definition is not None
                        else KPI_COLLECTOR_VERSION
                    )
                ),
                "source_version": str(
                    item.get("source_version")
                    or (
                        definition.source_version
                        if definition is not None
                        else KPI_SOURCE_VERSION
                    )
                ),
                "source": list(item.get("source") or []),
                "formula_version": str(item.get("formula_version") or ""),
                "definition_version": str(item.get("definition_version") or ""),
                "time_window": time_window,
                "window_start": window_start,
                "window_end": generated_at,
                "sample_size": current_sample,
                "confidence": float(item.get("confidence") or 0.0),
                "release_id": release.get("release_id"),
                "commit_sha": release.get("commit_sha"),
                "deployment_id": release.get("deployment_id"),
            }
        )
    return {
        "collector_version": KPI_COLLECTOR_VERSION,
        "source_version": KPI_SOURCE_VERSION,
        "release_id": release.get("release_id"),
        "commit_sha": release.get("commit_sha"),
        "deployment_id": release.get("deployment_id"),
        "window_start": min(window_starts) if window_starts else generated_at,
        "window_end": generated_at,
        "sample_size": sample_size,
        "confidence": float(health.get("confidence") or 0.0),
        "kpis": items,
    }


def build_health_preview(
    db: Session,
    *,
    org_slug: str,
    now_ts: int,
    objective_id: Optional[str],
    release_identity: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    current = build_current_snapshot(db, org_slug=org_slug, now_ts=now_ts)
    health = build_project_health_preview(
        current,
        target_overrides=target_override_map(
            db,
            org_slug=org_slug,
            objective_id=objective_id,
        ),
    )
    health["objective_id"] = objective_id
    health["release_identity"] = {
        key: (release_identity or {}).get(key)
        for key in (
            "release_id",
            "commit_sha",
            "deployment_id",
            "runtime_main_sha256",
            "migration_in_sync",
        )
    }
    provenance = _health_provenance(
        health,
        release_identity=release_identity,
    )
    health["provenance"] = provenance
    health["window_start"] = provenance["window_start"]
    health["window_end"] = provenance["window_end"]
    health["sample_size"] = provenance["sample_size"]
    return health


def build_diagnostics_preview(health: Mapping[str, Any]) -> dict[str, Any]:
    return build_diagnostic_preview(health)


def build_priorities_preview(
    health: Mapping[str, Any],
    *,
    objective_priority: int,
) -> dict[str, Any]:
    return build_priority_preview(health, objective_priority=objective_priority)


def build_proposal_previews(
    diagnostics: Mapping[str, Any],
    priorities: Mapping[str, Any],
    *,
    objective_id: Optional[str],
    selected_codes: Optional[set[str]] = None,
) -> dict[str, Any]:
    priorities_by_code = {
        item["kpi_code"]: item for item in priorities.get("items") or []
    }
    items: list[dict[str, Any]] = []
    for diagnostic in diagnostics.get("items") or []:
        code = str(diagnostic.get("kpi") or "")
        if selected_codes and code not in selected_codes:
            continue
        if diagnostic.get("recommended_action") != "technical_proposal_allowed":
            continue
        definition = get_kpi_definition(code)
        if definition is None or not definition.proposal_enabled:
            continue
        priority = priorities_by_code.get(code, {})
        items.append(
            {
                "id": f"preview:{code}",
                "title": f"Diagnosticar e corrigir {definition.name}",
                "status": "diagnostic_pending",
                "mode": "proposal_only",
                "objective_id": objective_id,
                "triggered_by_kpis": [code],
                "diagnosis": {
                    "root_cause": None,
                    "root_cause_status": diagnostic.get("root_cause_status"),
                    "confidence": diagnostic.get("confidence"),
                    "evidence": diagnostic.get("evidence"),
                    "hypotheses": diagnostic.get("hypotheses"),
                },
                "priority": priority,
                "expected_impact": {
                    code: f"aproximar de {definition.target:g} {definition.unit}"
                },
                "risk": "not_assessed",
                "files": [],
                "functions": [],
                "patch_minimum": "pending_root_cause_confirmation",
                "patch_premium": "pending_root_cause_confirmation",
                "diff_preview": None,
                "rollback": "Obrigatório antes de ready_for_review.",
                "tests": [],
                "success_criterion": f"{code} atinge meta com confiança suficiente.",
                "abort_criterion": "regressão, tenant leak, stream sem done ou migration inconsistente",
                "human_approval_required": True,
                "auto_apply": False,
                "write_executed": False,
            }
        )
    return {
        "proposal_mode": "proposal_only",
        "count": len(items),
        "items": items,
        "human_approval_required": True,
        "auto_apply": False,
        "write_executed": False,
    }


def _canonical_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def capture_health_snapshot(
    db: Session,
    *,
    snapshot_id: str,
    org_slug: str,
    objective_id: Optional[str],
    health: Mapping[str, Any],
    actor_ref: str,
    reason: str,
    now_ts: int,
    provenance_id: Optional[str] = None,
) -> dict[str, Any]:
    tables = _tables(db)
    required = {
        HEALTH_SNAPSHOTS_TABLE,
        HEALTH_PROVENANCE_TABLE,
        HEALTH_EVENTS_TABLE,
    }
    if not required.issubset(tables):
        raise RuntimeError("EVOLUTION_INTELLIGENCE_SCHEMA_UNAVAILABLE")
    release = dict(health.get("release_identity") or {})
    provenance = dict(health.get("provenance") or {})
    window_start = int(provenance.get("window_start") or health.get("window_start") or now_ts)
    window_end = int(provenance.get("window_end") or health.get("window_end") or now_ts)
    sample_size = max(0, int(provenance.get("sample_size") or health.get("sample_size") or 0))
    confidence = float(provenance.get("confidence") or health.get("confidence") or 0.0)
    provenance_payload = {
        **provenance,
        "snapshot_id": snapshot_id,
        "org_slug": org_slug,
        "objective_id": objective_id,
        "formula_version": health.get("formula_version"),
        "health_coverage": health.get("health_coverage", health.get("coverage")),
        "missing_dimensions": list(health.get("missing_dimensions") or []),
        "unknown_kpis": list(health.get("unknown_kpis") or []),
        "stale_kpis": list(health.get("stale_kpis") or []),
        "blockers": list(health.get("blockers") or health.get("blocker_kpis") or []),
    }
    content_sha256 = _canonical_sha256(
        {
            "snapshot": {
                "id": snapshot_id,
                "org_slug": org_slug,
                "objective_id": objective_id,
                "captured_at": now_ts,
                "window_start": window_start,
                "window_end": window_end,
                "score": health.get("score"),
                "confidence": confidence,
                "coverage": health.get("coverage", 0),
                "status": health.get("status", "unknown"),
                "production_go": bool(health.get("production_go", False)),
                "dimensions": health.get("dimensions") or {},
                "missing_kpis": health.get("missing_kpis") or [],
                "blocker_kpis": health.get("blocker_kpis") or [],
                "release_identity": release,
                "formula_version": health.get("formula_version"),
                "captured_by": actor_ref,
                "capture_reason": reason,
            },
            "provenance": provenance_payload,
        }
    )

    db.execute(
        text(
            f"""
            INSERT INTO {HEALTH_SNAPSHOTS_TABLE} (
                id, org_slug, objective_id, captured_at, window_start, window_end,
                project_health_score, confidence, data_coverage, status,
                production_go, dimensions_json, missing_kpis_json,
                blocker_kpis_json, release_id, commit_sha, deployment_id,
                runtime_main_sha256, formula_version, captured_by,
                capture_reason, created_at
            ) VALUES (
                :id, :org_slug, :objective_id, :captured_at, :window_start, :window_end,
                :project_health_score, :confidence, :data_coverage, :status,
                :production_go, :dimensions_json, :missing_kpis_json,
                :blocker_kpis_json, :release_id, :commit_sha, :deployment_id,
                :runtime_main_sha256, :formula_version, :captured_by,
                :capture_reason, :created_at
            )
            """
        ),
        {
            "id": snapshot_id,
            "org_slug": org_slug,
            "objective_id": objective_id,
            "captured_at": now_ts,
            "window_start": window_start,
            "window_end": window_end,
            "project_health_score": health.get("score"),
            "confidence": confidence,
            "data_coverage": health.get("coverage", 0),
            "status": health.get("status", "unknown"),
            "production_go": bool(health.get("production_go", False)),
            "dimensions_json": json.dumps(health.get("dimensions") or {}, sort_keys=True),
            "missing_kpis_json": json.dumps(health.get("missing_kpis") or [], sort_keys=True),
            "blocker_kpis_json": json.dumps(health.get("blocker_kpis") or [], sort_keys=True),
            "release_id": release.get("release_id"),
            "commit_sha": release.get("commit_sha"),
            "deployment_id": release.get("deployment_id"),
            "runtime_main_sha256": release.get("runtime_main_sha256"),
            "formula_version": health.get("formula_version"),
            "captured_by": actor_ref,
            "capture_reason": reason,
            "created_at": now_ts,
        },
    )
    db.execute(
        text(
            f"""
            INSERT INTO {HEALTH_PROVENANCE_TABLE} (
                id, org_slug, snapshot_id, collector_version, source_version,
                release_id, commit_sha, deployment_id, window_start, window_end,
                sample_size, confidence, provenance_json, content_sha256, created_at
            ) VALUES (
                :id, :org_slug, :snapshot_id, :collector_version, :source_version,
                :release_id, :commit_sha, :deployment_id, :window_start, :window_end,
                :sample_size, :confidence, :provenance_json, :content_sha256, :created_at
            )
            """
        ),
        {
            "id": provenance_id or f"ehsp_{snapshot_id}"[:96],
            "org_slug": org_slug,
            "snapshot_id": snapshot_id,
            "collector_version": str(
                provenance.get("collector_version") or KPI_COLLECTOR_VERSION
            ),
            "source_version": str(
                provenance.get("source_version") or KPI_SOURCE_VERSION
            ),
            "release_id": release.get("release_id"),
            "commit_sha": release.get("commit_sha"),
            "deployment_id": release.get("deployment_id"),
            "window_start": window_start,
            "window_end": window_end,
            "sample_size": sample_size,
            "confidence": confidence,
            "provenance_json": json.dumps(
                provenance_payload,
                ensure_ascii=False,
                sort_keys=True,
            ),
            "content_sha256": content_sha256,
            "created_at": now_ts,
        },
    )
    return {
        "id": snapshot_id,
        "org_slug": org_slug,
        "objective_id": objective_id,
        "captured_at": now_ts,
        "content_sha256": content_sha256,
        "immutable": True,
        "valid": True,
        "write_executed": True,
    }


def invalidate_health_snapshot(
    db: Session,
    *,
    event_id: str,
    org_slug: str,
    snapshot_id: str,
    actor_ref: str,
    reason: str,
    approval_id: str,
    now_ts: int,
) -> dict[str, Any]:
    tables = _tables(db)
    if HEALTH_SNAPSHOTS_TABLE not in tables or HEALTH_EVENTS_TABLE not in tables:
        raise RuntimeError("EVOLUTION_INTELLIGENCE_SCHEMA_UNAVAILABLE")
    snapshot = db.execute(
        text(
            f"""
            SELECT id
            FROM {HEALTH_SNAPSHOTS_TABLE}
            WHERE id = :snapshot_id AND org_slug = :org_slug
            LIMIT 1
            """
        ),
        {"snapshot_id": snapshot_id, "org_slug": org_slug},
    ).scalar_one_or_none()
    if snapshot is None:
        raise LookupError("HEALTH_SNAPSHOT_NOT_FOUND")
    existing = db.execute(
        text(
            f"""
            SELECT id
            FROM {HEALTH_EVENTS_TABLE}
            WHERE snapshot_id = :snapshot_id
              AND org_slug = :org_slug
              AND event_type = 'invalidated'
            LIMIT 1
            """
        ),
        {"snapshot_id": snapshot_id, "org_slug": org_slug},
    ).scalar_one_or_none()
    if existing is not None:
        raise ValueError("HEALTH_SNAPSHOT_ALREADY_INVALIDATED")
    db.execute(
        text(
            f"""
            INSERT INTO {HEALTH_EVENTS_TABLE} (
                id, org_slug, snapshot_id, event_type, reason, approval_id,
                actor_ref, metadata_json, created_at
            ) VALUES (
                :id, :org_slug, :snapshot_id, 'invalidated', :reason, :approval_id,
                :actor_ref, '{{}}', :created_at
            )
            """
        ),
        {
            "id": event_id,
            "org_slug": org_slug,
            "snapshot_id": snapshot_id,
            "reason": reason,
            "approval_id": approval_id,
            "actor_ref": actor_ref,
            "created_at": now_ts,
        },
    )
    return {
        "event_id": event_id,
        "snapshot_id": snapshot_id,
        "org_slug": org_slug,
        "event_type": "invalidated",
        "valid": False,
        "write_executed": True,
    }


def list_health_snapshot_events(
    db: Session,
    *,
    org_slug: str,
    snapshot_id: Optional[str],
    limit: int,
) -> list[dict[str, Any]]:
    if HEALTH_EVENTS_TABLE not in _tables(db):
        return []
    clauses = ["org_slug = :org_slug"]
    params: dict[str, Any] = {"org_slug": org_slug, "limit": limit}
    if snapshot_id:
        clauses.append("snapshot_id = :snapshot_id")
        params["snapshot_id"] = snapshot_id
    rows = db.execute(
        text(
            f"""
            SELECT id, org_slug, snapshot_id, event_type, reason, approval_id,
                   actor_ref, metadata_json, created_at
            FROM {HEALTH_EVENTS_TABLE}
            WHERE {' AND '.join(clauses)}
            ORDER BY created_at DESC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()
    result: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        try:
            item["metadata"] = json.loads(item.pop("metadata_json") or "{}")
        except Exception:
            item["metadata"] = {}
        result.append(item)
    return result


def list_health_snapshots(
    db: Session,
    *,
    org_slug: str,
    objective_id: Optional[str],
    limit: int,
) -> list[dict[str, Any]]:
    if HEALTH_SNAPSHOTS_TABLE not in _tables(db):
        return []
    clauses = ["s.org_slug=:org_slug"]
    params: dict[str, Any] = {"org_slug": org_slug, "limit": limit}
    if objective_id:
        clauses.append("s.objective_id=:objective_id")
        params["objective_id"] = objective_id
    rows = db.execute(
        text(
            f"""
            SELECT s.id, s.org_slug, s.objective_id, s.captured_at,
                   s.window_start, s.window_end, s.project_health_score,
                   s.confidence, s.data_coverage, s.status, s.production_go,
                   s.dimensions_json, s.missing_kpis_json, s.blocker_kpis_json,
                   s.release_id, s.commit_sha, s.deployment_id,
                   s.runtime_main_sha256, s.formula_version, s.captured_by,
                   s.capture_reason, s.created_at,
                   p.collector_version, p.source_version, p.sample_size,
                   p.provenance_json, p.content_sha256,
                   e.id AS invalidation_event_id,
                   e.reason AS invalidation_reason,
                   e.approval_id AS invalidation_approval_id,
                   e.actor_ref AS invalidated_by,
                   e.created_at AS invalidated_at
            FROM {HEALTH_SNAPSHOTS_TABLE} s
            LEFT JOIN {HEALTH_PROVENANCE_TABLE} p
              ON p.snapshot_id = s.id AND p.org_slug = s.org_slug
            LEFT JOIN {HEALTH_EVENTS_TABLE} e
              ON e.snapshot_id = s.id
             AND e.org_slug = s.org_slug
             AND e.event_type = 'invalidated'
            WHERE {' AND '.join(clauses)}
            ORDER BY s.captured_at DESC
            LIMIT :limit
            """
        ),
        params,
    ).mappings().all()
    result = []
    for row in rows:
        item = dict(row)
        for key in ("dimensions_json", "missing_kpis_json", "blocker_kpis_json"):
            try:
                item[key.removesuffix("_json")] = json.loads(item.pop(key) or "{}")
            except Exception:
                item[key.removesuffix("_json")] = {} if key == "dimensions_json" else []
        try:
            item["provenance"] = json.loads(item.pop("provenance_json") or "{}")
        except Exception:
            item["provenance"] = {}
        item["immutable"] = True
        item["valid"] = item.get("invalidation_event_id") is None
        result.append(item)
    return result


def list_evolution_audit_events(
    db: Session,
    *,
    org_slug: str,
    limit: int,
) -> list[dict[str, Any]]:
    if "audit_logs" not in _tables(db):
        return []
    rows = db.execute(
        text(
            """
            SELECT id, org_slug, user_id AS actor_ref, action, meta,
                   request_id, path, status_code, latency_ms, created_at
            FROM audit_logs
            WHERE org_slug = :org_slug
              AND action LIKE 'evolution_intelligence.%'
            ORDER BY created_at DESC
            LIMIT :limit
            """
        ),
        {"org_slug": org_slug, "limit": limit},
    ).mappings().all()
    result: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        try:
            item["metadata"] = json.loads(item.pop("meta") or "{}")
        except Exception:
            item["metadata"] = {}
        result.append(item)
    return result
