from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Literal, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.evolution_signals import (
    AgentCapabilityEvaluationIn,
    AgentCapabilityEvaluationOut,
    EvolutionSignalCaptureIn,
    EvolutionSignalCaptureOut,
    EvolutionSignalHistoryOut,
    EvolutionSignalsCurrentOut,
)
from app.services.evolution_signal_service import (
    FORMULA_VERSION,
    METRIC_KEYS,
    build_current_snapshot,
    capture_snapshot,
    list_history,
)


@dataclass(frozen=True)
class EvolutionSignalsRouterDeps:
    get_db: Callable[..., Any]
    require_admin_access: Callable[..., Any]
    get_request_org: Callable[[dict[str, Any], Optional[str]], str]
    new_id: Callable[[], str]
    now_ts: Callable[[], int]
    logger: Any


def _flag(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _actor_ref(admin: Any) -> str:
    if not isinstance(admin, dict):
        return "admin:unknown"
    return str(
        admin.get("id")
        or admin.get("user_id")
        or admin.get("email")
        or admin.get("sub")
        or "admin:unknown"
    )[:180]


def _write_audit(
    db: Session,
    *,
    deps: EvolutionSignalsRouterDeps,
    request: Request,
    org_slug: str,
    actor_ref: str,
    action: str,
    meta: dict[str, Any],
    status_code: int = 200,
) -> None:
    db.execute(
        text(
            """
            INSERT INTO audit_logs (
                id, org_slug, user_id, action, meta, request_id,
                path, status_code, latency_ms, created_at
            ) VALUES (
                :id, :org_slug, :user_id, :action, :meta, :request_id,
                :path, :status_code, 0, :created_at
            )
            """
        ),
        {
            "id": deps.new_id(),
            "org_slug": org_slug,
            "user_id": actor_ref,
            "action": action,
            "meta": json.dumps(meta, ensure_ascii=False, sort_keys=True),
            "request_id": (
                request.headers.get("x-request-id")
                or request.headers.get("x-railway-request-id")
                or deps.new_id()
            ),
            "path": request.url.path,
            "status_code": status_code,
            "created_at": deps.now_ts(),
        },
    )


def build_evolution_signals_router(deps: EvolutionSignalsRouterDeps) -> APIRouter:
    router = APIRouter(
        prefix="/api/admin/evolution",
        tags=["admin-evolution-signals"],
    )

    @router.get("/signals/current", response_model=EvolutionSignalsCurrentOut)
    def current_signals(
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        org = deps.get_request_org(admin, x_org_slug)
        snapshot = build_current_snapshot(db, org_slug=org, now_ts=deps.now_ts())
        return EvolutionSignalsCurrentOut(**snapshot)

    @router.get("/signals/history", response_model=EvolutionSignalHistoryOut)
    def signal_history(
        days: int = Query(default=30, ge=1, le=365),
        metric_key: Optional[str] = Query(default=None, max_length=80),
        scope_type: Optional[Literal["platform", "agent"]] = Query(default=None),
        limit: int = Query(default=2000, ge=1, le=5000),
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        if metric_key and metric_key not in METRIC_KEYS:
            raise HTTPException(status_code=422, detail="INVALID_EVOLUTION_METRIC_KEY")
        org = deps.get_request_org(admin, x_org_slug)
        rows = list_history(
            db,
            org_slug=org,
            cutoff=deps.now_ts() - days * 86_400,
            metric_key=metric_key,
            scope_type=scope_type,
            limit=limit,
        )
        return EvolutionSignalHistoryOut(
            org_slug=org,
            count=len(rows),
            items=rows,
            write_executed=False,
        )

    @router.post("/signals/snapshots/capture", response_model=EvolutionSignalCaptureOut)
    def capture_current_signals(
        payload: EvolutionSignalCaptureIn,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        if not payload.approved:
            raise HTTPException(status_code=409, detail="HUMAN_APPROVAL_REQUIRED")
        if not _flag("EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED", False):
            raise HTTPException(status_code=403, detail="EVOLUTION_SIGNAL_CAPTURE_DISABLED")

        org = deps.get_request_org(admin, x_org_slug)
        actor = _actor_ref(admin)
        now = deps.now_ts()
        snapshot = build_current_snapshot(db, org_slug=org, now_ts=now)
        group_id = f"esnap_{deps.new_id()[:16]}"
        try:
            metrics_count, agents_count = capture_snapshot(
                db,
                snapshot=snapshot,
                snapshot_group_id=group_id,
                org_slug=org,
                actor_ref=actor,
                reason=payload.reason,
                now_ts=now,
                id_factory=deps.new_id,
            )
            _write_audit(
                db,
                deps=deps,
                request=request,
                org_slug=org,
                actor_ref=actor,
                action="evolution_signals.snapshot.captured",
                meta={
                    "snapshot_group_id": group_id,
                    "formula_version": FORMULA_VERSION,
                    "metrics_persisted": metrics_count,
                    "agent_metrics_persisted": agents_count,
                },
            )
            db.commit()
        except Exception:
            db.rollback()
            deps.logger.exception(
                "EVOLUTION_SIGNALS_CAPTURE_FAILED org=%s actor=%s",
                org,
                actor,
            )
            raise HTTPException(status_code=500, detail="EVOLUTION_SIGNAL_CAPTURE_FAILED")

        return EvolutionSignalCaptureOut(
            captured=True,
            snapshot_group_id=group_id,
            metrics_persisted=metrics_count,
            agent_metrics_persisted=agents_count,
            generated_at=now,
            write_executed=True,
        )

    @router.post(
        "/agent-evaluations",
        response_model=AgentCapabilityEvaluationOut,
    )
    def record_agent_evaluation(
        payload: AgentCapabilityEvaluationIn,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        admin=Depends(deps.require_admin_access),
        db: Session = Depends(deps.get_db),
    ):
        if not _flag("EVOLUTION_AGENT_EVAL_WRITE_ENABLED", False):
            raise HTTPException(status_code=403, detail="EVOLUTION_AGENT_EVAL_WRITE_DISABLED")

        org = deps.get_request_org(admin, x_org_slug)
        actor = _actor_ref(admin)
        exists = db.execute(
            text(
                """
                SELECT 1 FROM agents
                WHERE id = :agent_id AND org_slug = :org_slug
                LIMIT 1
                """
            ),
            {"agent_id": payload.agent_id, "org_slug": org},
        ).scalar_one_or_none()
        if exists is None:
            raise HTTPException(status_code=404, detail="AGENT_NOT_FOUND")

        evaluation_id = f"aeval_{deps.new_id()[:16]}"
        now = deps.now_ts()
        try:
            db.execute(
                text(
                    """
                    INSERT INTO agent_capability_evaluations (
                        evaluation_id, org_slug, agent_id, capability_id,
                        evaluation_key, status, score, confidence,
                        evidence_ref, notes, evaluator_ref, created_at
                    ) VALUES (
                        :evaluation_id, :org_slug, :agent_id, :capability_id,
                        :evaluation_key, :status, :score, :confidence,
                        :evidence_ref, :notes, :evaluator_ref, :created_at
                    )
                    """
                ),
                {
                    "evaluation_id": evaluation_id,
                    "org_slug": org,
                    "agent_id": payload.agent_id,
                    "capability_id": payload.capability_id,
                    "evaluation_key": payload.evaluation_key,
                    "status": payload.status,
                    "score": payload.score,
                    "confidence": payload.confidence,
                    "evidence_ref": payload.evidence_ref,
                    "notes": payload.notes,
                    "evaluator_ref": actor,
                    "created_at": now,
                },
            )
            _write_audit(
                db,
                deps=deps,
                request=request,
                org_slug=org,
                actor_ref=actor,
                action="evolution_signals.agent_evaluation.recorded",
                meta={
                    "evaluation_id": evaluation_id,
                    "agent_id": payload.agent_id,
                    "capability_id": payload.capability_id,
                    "evaluation_key": payload.evaluation_key,
                    "status": payload.status,
                    "score": payload.score,
                    "confidence": payload.confidence,
                    "evidence_ref": payload.evidence_ref,
                },
            )
            db.commit()
        except Exception:
            db.rollback()
            deps.logger.exception(
                "EVOLUTION_AGENT_EVALUATION_FAILED org=%s agent=%s",
                org,
                payload.agent_id,
            )
            raise HTTPException(status_code=500, detail="EVOLUTION_AGENT_EVALUATION_FAILED")

        return AgentCapabilityEvaluationOut(
            evaluation_id=evaluation_id,
            org_slug=org,
            agent_id=payload.agent_id,
            capability_id=payload.capability_id,
            evaluation_key=payload.evaluation_key,
            status=payload.status,
            score=payload.score,
            confidence=payload.confidence,
            created_at=now,
            write_executed=True,
        )

    return router
