from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.evolution.intelligence.governance import (
    load_evolution_governance_config,
    validate_evolution_governance_config,
)
from app.evolution.intelligence.kpi_registry import (
    KPI_REGISTRY_VERSION,
    get_kpi_definition,
)
from app.schemas.evolution_intelligence import (
    DiagnosticPreviewOut,
    HealthPreviewOut,
    HealthSnapshotCaptureIn,
    HealthSnapshotInvalidateIn,
    HealthSnapshotListOut,
    KPIRegistryOut,
    KPITargetUpsertIn,
    ObjectiveCreateIn,
    ObjectiveListOut,
    ObjectiveOut,
    ObjectiveUpdateIn,
    PriorityPreviewOut,
    ProposalPreviewIn,
    ProposalPreviewOut,
)
from app.services.evolution_intelligence_service import (
    build_diagnostics_preview,
    build_health_preview,
    build_inventory,
    build_priorities_preview,
    build_proposal_previews,
    capture_health_snapshot,
    create_objective,
    foundation_schema_status,
    get_objective,
    invalidate_health_snapshot,
    list_evolution_audit_events,
    list_health_snapshot_events,
    list_health_snapshots,
    list_objectives,
    list_target_history,
    update_objective,
    upsert_target,
)


@dataclass(frozen=True)
class EvolutionIntelligenceRouterDeps:
    get_db: Callable[..., Any]
    require_admin_access: Callable[..., Any]
    get_request_org: Callable[[dict[str, Any], Optional[str]], str]
    new_id: Callable[[], str]
    now_ts: Callable[[], int]
    actor_reference: Callable[[Any], str]
    logger: Any


def _actor_ref(admin: Any, deps: EvolutionIntelligenceRouterDeps) -> str:
    if not isinstance(admin, dict):
        return "actor:unknown"
    value = (
        admin.get("id")
        or admin.get("user_id")
        or admin.get("email")
        or admin.get("sub")
    )
    return deps.actor_reference(value)


def _governance() -> dict[str, Any]:
    try:
        return validate_evolution_governance_config(
            load_evolution_governance_config()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "EVOLUTION_GOVERNANCE_INVALID",
                "error_type": exc.__class__.__name__,
            },
        ) from exc


def _ensure_center_enabled() -> dict[str, Any]:
    cfg = _governance()
    if not cfg["center_enabled"]:
        raise HTTPException(status_code=404, detail="EVOLUTION_CENTER_DISABLED")
    return cfg


def _require_config_write(payload_approved: bool) -> dict[str, Any]:
    cfg = _ensure_center_enabled()
    if not payload_approved:
        raise HTTPException(status_code=409, detail="HUMAN_APPROVAL_REQUIRED")
    if not cfg["config_write_enabled"]:
        raise HTTPException(
            status_code=403,
            detail="EVOLUTION_CONFIG_WRITE_DISABLED",
        )
    if not cfg["human_approval_required"]:
        raise HTTPException(status_code=503, detail="EVOLUTION_GOVERNANCE_INVALID")
    return cfg


def _write_audit(
    db: Session,
    *,
    deps: EvolutionIntelligenceRouterDeps,
    request: Request,
    org_slug: str,
    actor_ref_value: str,
    action: str,
    meta: dict[str, Any],
) -> None:
    db.execute(
        text(
            """
            INSERT INTO audit_logs (
                id, org_slug, user_id, action, meta, request_id,
                path, status_code, latency_ms, created_at
            ) VALUES (
                :id, :org_slug, :user_id, :action, :meta, :request_id,
                :path, 200, 0, :created_at
            )
            """
        ),
        {
            "id": deps.new_id(),
            "org_slug": org_slug,
            "user_id": actor_ref_value,
            "action": action,
            "meta": json.dumps(meta, ensure_ascii=False, sort_keys=True),
            "request_id": (
                request.headers.get("x-request-id")
                or request.headers.get("x-railway-request-id")
                or deps.new_id()
            ),
            "path": request.url.path,
            "created_at": deps.now_ts(),
        },
    )


def build_evolution_intelligence_router(
    deps: EvolutionIntelligenceRouterDeps,
) -> APIRouter:
    router = APIRouter(
        prefix="/api/admin/evolution/intelligence",
        tags=["admin-evolution-intelligence"],
    )

    @router.get("/runtime")
    def evolution_runtime(
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        cfg = _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        boot_cfg = dict(
            getattr(request.app.state, "evolution_intelligence_config", {}) or {}
        )
        comparable_keys = (
            "version",
            "center_enabled",
            "kpi_collection_enabled",
            "config_write_enabled",
            "health_snapshot_write_enabled",
            "proposal_generation_enabled",
            "proposal_only",
            "diff_preview_enabled",
            "write_enabled",
            "auto_apply_enabled",
            "human_approval_required",
            "rollback_required",
        )
        governance_consistent = bool(boot_cfg) and all(
            boot_cfg.get(key) == cfg.get(key)
            for key in comparable_keys
        )
        governance_validated = (
            getattr(
                request.app.state,
                "evolution_intelligence_status",
                None,
            )
            == "validated"
            and bool(cfg.get("valid"))
        )
        runtime_identity = {
            "evolution_center_enabled": cfg["center_enabled"],
            "evolution_proposal_only": cfg["proposal_only"],
            "evolution_write_enabled": cfg["write_enabled"],
            "evolution_auto_apply_enabled": cfg["auto_apply_enabled"],
            "evolution_config_write_enabled": cfg["config_write_enabled"],
            "evolution_snapshot_write_enabled": cfg[
                "health_snapshot_write_enabled"
            ],
            "evolution_proposal_generation_enabled": cfg[
                "proposal_generation_enabled"
            ],
            "evolution_governance_validated": governance_validated,
            "evolution_governance_consistent": governance_consistent,
            "kpi_registry_version": KPI_REGISTRY_VERSION,
        }
        return {
            "org_slug": org,
            **runtime_identity,
            "runtime_governance_identity": runtime_identity,
            "governance": cfg,
            "boot_governance": {
                key: boot_cfg.get(key)
                for key in comparable_keys
            },
            "schema": foundation_schema_status(db),
            "write_executed": False,
        }

    @router.get("/inventory", response_model=KPIRegistryOut)
    def inventory(
        objective_id: Optional[str] = Query(default=None, max_length=96),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        cfg = _ensure_center_enabled()
        if not cfg["kpi_collection_enabled"]:
            raise HTTPException(
                status_code=403,
                detail="EVOLUTION_KPI_COLLECTION_DISABLED",
            )
        org = deps.get_request_org(admin, x_org_slug)
        return KPIRegistryOut(
            **build_inventory(
                db,
                org_slug=org,
                now_ts=deps.now_ts(),
                objective_id=objective_id,
            )
        )

    @router.get("/objectives", response_model=ObjectiveListOut)
    def objectives(
        status: Optional[str] = Query(default=None, max_length=24),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        items = list_objectives(db, org_slug=org, status=status)
        return ObjectiveListOut(
            org_slug=org,
            count=len(items),
            items=[ObjectiveOut(**item, write_executed=False) for item in items],
            write_executed=False,
        )

    @router.get("/objectives/{objective_id}", response_model=ObjectiveOut)
    def objective_detail(
        objective_id: str,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        item = get_objective(db, org_slug=org, objective_id=objective_id)
        if item is None:
            raise HTTPException(status_code=404, detail="OBJECTIVE_NOT_FOUND")
        return ObjectiveOut(**item, write_executed=False)

    @router.post("/objectives", response_model=ObjectiveOut)
    def objective_create(
        payload: ObjectiveCreateIn,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _require_config_write(payload.approved)
        org = deps.get_request_org(admin, x_org_slug)
        actor = _actor_ref(admin, deps)
        objective_id = f"eobj_{deps.new_id()[:20]}"
        try:
            item = create_objective(
                db,
                org_slug=org,
                objective_id=objective_id,
                payload=payload.model_dump(),
                actor_ref=actor,
                now_ts=deps.now_ts(),
            )
            _write_audit(
                db,
                deps=deps,
                request=request,
                org_slug=org,
                actor_ref_value=actor,
                action="evolution_intelligence.objective.created",
                meta={
                    "objective_id": objective_id,
                    "category": payload.category,
                    "priority": payload.priority,
                    "proposal_policy": "proposal_only",
                },
            )
            db.commit()
        except ValueError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except HTTPException:
            db.rollback()
            raise
        except Exception as exc:
            db.rollback()
            deps.logger.exception(
                "EVOLUTION_OBJECTIVE_CREATE_FAILED org=%s actor=%s",
                org,
                actor,
            )
            raise HTTPException(
                status_code=500,
                detail="EVOLUTION_OBJECTIVE_CREATE_FAILED",
            ) from exc
        return ObjectiveOut(**item, write_executed=True)

    @router.patch("/objectives/{objective_id}", response_model=ObjectiveOut)
    def objective_update(
        objective_id: str,
        payload: ObjectiveUpdateIn,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _require_config_write(payload.approved)
        org = deps.get_request_org(admin, x_org_slug)
        actor = _actor_ref(admin, deps)
        try:
            item = update_objective(
                db,
                org_slug=org,
                objective_id=objective_id,
                payload=payload.model_dump(exclude_unset=True),
                actor_ref=actor,
                now_ts=deps.now_ts(),
            )
            if item is None:
                raise HTTPException(status_code=404, detail="OBJECTIVE_NOT_FOUND")
            _write_audit(
                db,
                deps=deps,
                request=request,
                org_slug=org,
                actor_ref_value=actor,
                action="evolution_intelligence.objective.updated",
                meta={
                    "objective_id": objective_id,
                    "updated_fields": sorted(
                        key
                        for key in payload.model_fields_set
                        if key != "approved"
                    ),
                },
            )
            db.commit()
        except ValueError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except HTTPException:
            db.rollback()
            raise
        except Exception as exc:
            db.rollback()
            deps.logger.exception(
                "EVOLUTION_OBJECTIVE_UPDATE_FAILED org=%s objective=%s",
                org,
                objective_id,
            )
            raise HTTPException(
                status_code=500,
                detail="EVOLUTION_OBJECTIVE_UPDATE_FAILED",
            ) from exc
        return ObjectiveOut(**item, write_executed=True)

    @router.get("/kpis", response_model=KPIRegistryOut)
    def kpis(
        objective_id: Optional[str] = Query(default=None, max_length=96),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        return KPIRegistryOut(
            **build_inventory(
                db,
                org_slug=org,
                now_ts=deps.now_ts(),
                objective_id=objective_id,
            )
        )

    @router.get("/kpis/{kpi_code}")
    def kpi_detail(
        kpi_code: str,
        objective_id: Optional[str] = Query(default=None, max_length=96),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        inventory_payload = build_inventory(
            db,
            org_slug=org,
            now_ts=deps.now_ts(),
            objective_id=objective_id,
        )
        definition = get_kpi_definition(kpi_code)
        if definition is None:
            raise HTTPException(status_code=404, detail="KPI_NOT_FOUND")
        target = next(
            (
                row
                for row in inventory_payload["targets"]
                if row["kpi_code"] == kpi_code
            ),
            None,
        )
        return {
            "org_slug": org,
            "definition": definition.to_dict(),
            "target": target,
            "write_executed": False,
        }

    @router.put("/targets")
    def target_upsert(
        payload: KPITargetUpsertIn,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _require_config_write(payload.approved)
        org = deps.get_request_org(admin, x_org_slug)
        actor = _actor_ref(admin, deps)
        try:
            item = upsert_target(
                db,
                org_slug=org,
                target_id=f"etgt_{deps.new_id()[:20]}",
                version_id=f"etgv_{deps.new_id()[:20]}",
                payload=payload.model_dump(),
                actor_ref=actor,
                now_ts=deps.now_ts(),
            )
            _write_audit(
                db,
                deps=deps,
                request=request,
                org_slug=org,
                actor_ref_value=actor,
                action="evolution_intelligence.target.version_created",
                meta={
                    "target_id": item.get("id"),
                    "history_id": item.get("history_id"),
                    "version": item.get("version"),
                    "objective_id": payload.objective_id,
                    "kpi_code": payload.kpi_code,
                    "target_value": payload.target_value,
                    "change_reason": payload.change_reason,
                    "approval_id": payload.approval_id,
                    "auto_apply_enabled": False,
                },
            )
            db.commit()
        except LookupError as exc:
            db.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:
            db.rollback()
            deps.logger.exception(
                "EVOLUTION_TARGET_UPSERT_FAILED org=%s kpi=%s",
                org,
                payload.kpi_code,
            )
            raise HTTPException(
                status_code=500,
                detail="EVOLUTION_TARGET_UPSERT_FAILED",
            ) from exc
        return {**item, "write_executed": True}

    @router.get("/targets/history")
    def target_history(
        objective_id: Optional[str] = Query(default=None, max_length=96),
        kpi_code: Optional[str] = Query(default=None, max_length=128),
        limit: int = Query(default=200, ge=1, le=2000),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        items = list_target_history(
            db,
            org_slug=org,
            objective_id=objective_id,
            kpi_code=kpi_code,
            limit=limit,
        )
        return {
            "org_slug": org,
            "count": len(items),
            "items": items,
            "write_executed": False,
        }

    def _health(
        *,
        request: Request,
        db: Session,
        org: str,
        objective_id: Optional[str],
    ) -> dict[str, Any]:
        identity = getattr(request.app.state, "runtime_identity", {}) or {}
        return build_health_preview(
            db,
            org_slug=org,
            now_ts=deps.now_ts(),
            objective_id=objective_id,
            release_identity=identity,
        )

    @router.get("/health/preview", response_model=HealthPreviewOut)
    def health_preview(
        request: Request,
        objective_id: Optional[str] = Query(default=None, max_length=96),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        cfg = _ensure_center_enabled()
        if not cfg["kpi_collection_enabled"]:
            raise HTTPException(
                status_code=403,
                detail="EVOLUTION_KPI_COLLECTION_DISABLED",
            )
        org = deps.get_request_org(admin, x_org_slug)
        return HealthPreviewOut(
            **_health(
                request=request,
                db=db,
                org=org,
                objective_id=objective_id,
            )
        )

    @router.get("/diagnostics/preview", response_model=DiagnosticPreviewOut)
    def diagnostics_preview(
        request: Request,
        objective_id: Optional[str] = Query(default=None, max_length=96),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        health = _health(
            request=request,
            db=db,
            org=org,
            objective_id=objective_id,
        )
        result = build_diagnostics_preview(health)
        return DiagnosticPreviewOut(org_slug=org, **result)

    @router.get("/priorities/preview", response_model=PriorityPreviewOut)
    def priorities_preview(
        request: Request,
        objective_id: Optional[str] = Query(default=None, max_length=96),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        objective = (
            get_objective(db, org_slug=org, objective_id=objective_id)
            if objective_id
            else None
        )
        if objective_id and objective is None:
            raise HTTPException(status_code=404, detail="OBJECTIVE_NOT_FOUND")
        health = _health(
            request=request,
            db=db,
            org=org,
            objective_id=objective_id,
        )
        result = build_priorities_preview(
            health,
            objective_priority=int((objective or {}).get("priority") or 80),
        )
        return PriorityPreviewOut(org_slug=org, **result)

    @router.post("/proposals/preview", response_model=ProposalPreviewOut)
    def proposals_preview(
        payload: ProposalPreviewIn,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        cfg = _ensure_center_enabled()
        if not cfg["proposal_generation_enabled"]:
            raise HTTPException(
                status_code=403,
                detail="EVOLUTION_PROPOSAL_GENERATION_DISABLED",
            )
        if not cfg["proposal_only"]:
            raise HTTPException(status_code=503, detail="EVOLUTION_GOVERNANCE_INVALID")
        org = deps.get_request_org(admin, x_org_slug)
        objective = (
            get_objective(db, org_slug=org, objective_id=payload.objective_id)
            if payload.objective_id
            else None
        )
        if payload.objective_id and objective is None:
            raise HTTPException(status_code=404, detail="OBJECTIVE_NOT_FOUND")
        health = _health(
            request=request,
            db=db,
            org=org,
            objective_id=payload.objective_id,
        )
        diagnostics = build_diagnostics_preview(health)
        priorities = build_priorities_preview(
            health,
            objective_priority=int((objective or {}).get("priority") or 80),
        )
        result = build_proposal_previews(
            diagnostics,
            priorities,
            objective_id=payload.objective_id,
            selected_codes=set(payload.kpi_codes or []),
        )
        return ProposalPreviewOut(org_slug=org, **result)

    @router.post("/health/snapshots/capture")
    def health_snapshot_capture(
        payload: HealthSnapshotCaptureIn,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        cfg = _ensure_center_enabled()
        if not payload.approved:
            raise HTTPException(status_code=409, detail="HUMAN_APPROVAL_REQUIRED")
        if not cfg["health_snapshot_write_enabled"]:
            raise HTTPException(
                status_code=403,
                detail="EVOLUTION_HEALTH_SNAPSHOT_WRITE_DISABLED",
            )
        org = deps.get_request_org(admin, x_org_slug)
        if payload.objective_id and get_objective(
            db,
            org_slug=org,
            objective_id=payload.objective_id,
        ) is None:
            raise HTTPException(status_code=404, detail="OBJECTIVE_NOT_FOUND")
        actor = _actor_ref(admin, deps)
        health = _health(
            request=request,
            db=db,
            org=org,
            objective_id=payload.objective_id,
        )
        snapshot_id = f"ehs_{deps.new_id()[:20]}"
        try:
            result = capture_health_snapshot(
                db,
                snapshot_id=snapshot_id,
                provenance_id=f"ehsp_{deps.new_id()[:20]}",
                org_slug=org,
                objective_id=payload.objective_id,
                health=health,
                actor_ref=actor,
                reason=payload.reason,
                now_ts=deps.now_ts(),
            )
            _write_audit(
                db,
                deps=deps,
                request=request,
                org_slug=org,
                actor_ref_value=actor,
                action="evolution_intelligence.health_snapshot.captured",
                meta={
                    "snapshot_id": snapshot_id,
                    "objective_id": payload.objective_id,
                    "score": health.get("score"),
                    "confidence": health.get("confidence"),
                    "coverage": health.get("coverage"),
                    "production_go": health.get("production_go"),
                    "content_sha256": result.get("content_sha256"),
                    "collector_version": (
                        health.get("provenance") or {}
                    ).get("collector_version"),
                    "source_version": (
                        health.get("provenance") or {}
                    ).get("source_version"),
                    "immutable": True,
                },
            )
            db.commit()
        except Exception as exc:
            db.rollback()
            deps.logger.exception(
                "EVOLUTION_HEALTH_SNAPSHOT_CAPTURE_FAILED org=%s",
                org,
            )
            raise HTTPException(
                status_code=500,
                detail="EVOLUTION_HEALTH_SNAPSHOT_CAPTURE_FAILED",
            ) from exc
        return result

    @router.get("/health/snapshots", response_model=HealthSnapshotListOut)
    def health_snapshots(
        objective_id: Optional[str] = Query(default=None, max_length=96),
        limit: int = Query(default=100, ge=1, le=1000),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        items = list_health_snapshots(
            db,
            org_slug=org,
            objective_id=objective_id,
            limit=limit,
        )
        return HealthSnapshotListOut(
            org_slug=org,
            count=len(items),
            items=items,
            write_executed=False,
        )

    @router.post("/health/snapshots/{snapshot_id}/invalidate")
    def health_snapshot_invalidate(
        snapshot_id: str,
        payload: HealthSnapshotInvalidateIn,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        cfg = _ensure_center_enabled()
        if not cfg["health_snapshot_write_enabled"]:
            raise HTTPException(
                status_code=403,
                detail="EVOLUTION_HEALTH_SNAPSHOT_WRITE_DISABLED",
            )
        org = deps.get_request_org(admin, x_org_slug)
        actor = _actor_ref(admin, deps)
        try:
            result = invalidate_health_snapshot(
                db,
                event_id=f"ehse_{deps.new_id()[:20]}",
                org_slug=org,
                snapshot_id=snapshot_id,
                actor_ref=actor,
                reason=payload.reason,
                approval_id=payload.approval_id,
                now_ts=deps.now_ts(),
            )
            _write_audit(
                db,
                deps=deps,
                request=request,
                org_slug=org,
                actor_ref_value=actor,
                action="evolution_intelligence.health_snapshot.invalidated",
                meta={
                    "snapshot_id": snapshot_id,
                    "event_id": result.get("event_id"),
                    "approval_id": payload.approval_id,
                    "immutable_snapshot_preserved": True,
                },
            )
            db.commit()
        except LookupError as exc:
            db.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:
            db.rollback()
            deps.logger.exception(
                "EVOLUTION_HEALTH_SNAPSHOT_INVALIDATE_FAILED org=%s snapshot=%s",
                org,
                snapshot_id,
            )
            raise HTTPException(
                status_code=500,
                detail="EVOLUTION_HEALTH_SNAPSHOT_INVALIDATE_FAILED",
            ) from exc
        return result

    @router.get("/health/snapshots/events")
    def health_snapshot_events(
        snapshot_id: Optional[str] = Query(default=None, max_length=96),
        limit: int = Query(default=200, ge=1, le=2000),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        items = list_health_snapshot_events(
            db,
            org_slug=org,
            snapshot_id=snapshot_id,
            limit=limit,
        )
        return {
            "org_slug": org,
            "count": len(items),
            "items": items,
            "write_executed": False,
        }

    @router.get("/audit")
    def audit_events(
        limit: int = Query(default=200, ge=1, le=2000),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        _ensure_center_enabled()
        org = deps.get_request_org(admin, x_org_slug)
        items = list_evolution_audit_events(
            db,
            org_slug=org,
            limit=limit,
        )
        return {
            "org_slug": org,
            "count": len(items),
            "items": items,
            "write_executed": False,
        }

    return router
