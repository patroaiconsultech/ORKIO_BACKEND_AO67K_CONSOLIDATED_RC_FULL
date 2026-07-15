from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import urllib.parse
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import Response
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import File, Message, Thread
from ..schemas.document_artifacts import DocumentArtifactGenerateIn
from ..services.document_artifact_service import (
    DocumentArtifactConcurrencyError,
    DocumentArtifactLimitError,
    DocumentArtifactLimits,
    DocumentArtifactTimeoutError,
    DocumentArtifactWorkerError,
    generate_document_artifact_isolated,
)
from ..services.document_artifact_command_service import (
    DocumentArtifactCommandDeps,
    DocumentArtifactThreadNotFound,
    execute_document_artifact_command,
)
from ..services.document_context_service import build_thread_document_context
from ..services.document_governance_service import (
    DocioAuditPersistenceError,
    DocioCoordinationUnavailable,
    DocioGovernanceError,
    DocioLockUnavailable,
    DocioQuotaExceeded,
    DocioReindexError,
    commit_failure_audit,
    distributed_locks,
    enforce_prospective_quota,
    last_successful_reindex_at,
    stage_audit,
    stage_binary_reindex,
    stage_text_index,
)


@dataclass(frozen=True)
class DocumentArtifactRouterDeps:
    get_current_user: Callable[..., Dict[str, Any]]
    get_request_org: Callable[[Dict[str, Any], Optional[str]], str]
    require_thread_member: Callable[[Session, str, str, str], Any]
    check_thread_member: Callable[[Session, str, str, str], Any]
    new_id: Callable[[], str]
    now_ts: Callable[[], int]
    logger: logging.Logger
    session_factory: Callable[[], Session]


def _request_id(request: Request) -> str:
    return (
        request.headers.get("x-request-id")
        or request.headers.get("x-railway-request-id")
        or uuid.uuid4().hex
    )


def _latency_ms(started: float) -> int:
    return max(0, int((time.monotonic() - started) * 1000))


def _bounded_reindex_interval() -> int:
    raw = os.getenv("ORKIO_DOCIO_REINDEX_MIN_INTERVAL_SECONDS", "300")
    try:
        value = int(raw)
    except (TypeError, ValueError):
        value = 300
    return max(5, min(value, 86_400))


async def _read_limited_json_body(
    request: Request,
    *,
    max_bytes: int,
) -> Dict[str, Any]:
    content_encoding = str(request.headers.get("content-encoding") or "").strip().lower()
    if content_encoding not in {"", "identity"}:
        raise HTTPException(status_code=415, detail="compressed_request_body_not_supported")

    content_length = request.headers.get("content-length")
    if content_length:
        try:
            declared = int(content_length)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="invalid_content_length") from exc
        if declared < 0:
            raise HTTPException(status_code=400, detail="invalid_content_length")
        if declared > max_bytes:
            raise HTTPException(status_code=413, detail="request_body_too_large")

    chunks = []
    received = 0
    async for chunk in request.stream():
        received += len(chunk)
        if received > max_bytes:
            raise HTTPException(status_code=413, detail="request_body_too_large")
        if chunk:
            chunks.append(bytes(chunk))

    raw = b"".join(chunks)
    if not raw:
        raise HTTPException(status_code=400, detail="request_body_required")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail="invalid_json_body") from exc
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail="json_object_required")
    return payload


def _content_disposition(filename: str) -> str:
    raw = str(filename or "orkio_document").replace("\r", " ").replace("\n", " ")
    raw = raw.replace('"', "'").strip() or "orkio_document"
    ascii_fallback = raw.encode("ascii", "ignore").decode("ascii")
    ascii_fallback = "".join(
        char if char.isalnum() or char in "._- " else "_"
        for char in ascii_fallback
    ).strip(" .")[:120] or "orkio_document"
    encoded = urllib.parse.quote(raw, safe="")
    return (
        f'attachment; filename="{ascii_fallback}"; '
        f"filename*=UTF-8''{encoded}"
    )


def build_document_artifacts_router(
    deps: DocumentArtifactRouterDeps,
) -> APIRouter:
    router = APIRouter(tags=["document-artifacts"])

    def _persist_failure_or_raise(
        db: Session,
        *,
        org: str,
        user_id: Optional[str],
        action: str,
        request_id: str,
        path: str,
        status_code: int,
        started: float,
        detail: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload = dict(meta or {})
        payload["detail"] = detail
        try:
            commit_failure_audit(
                db,
                audit_id=deps.new_id(),
                org=org,
                user_id=user_id,
                action=action,
                request_id=request_id,
                path=path,
                status_code=status_code,
                latency_ms=_latency_ms(started),
                now_ts=deps.now_ts(),
                meta=payload,
            )
        except DocioAuditPersistenceError as exc:
            deps.logger.exception(
                "DOCIO_AUDIT_PERSISTENCE_FAILED action=%s org=%s request_id=%s",
                action,
                org,
                request_id,
            )
            raise HTTPException(status_code=503, detail="audit_persistence_failed") from exc

    def _require_file_read_access(
        db: Session,
        org: str,
        file_row: File,
        user: Dict[str, Any],
    ) -> None:
        if user.get("role") == "admin":
            return
        user_id = str(user.get("sub") or "")
        if (
            getattr(file_row, "uploader_id", None)
            and str(getattr(file_row, "uploader_id", "")) == user_id
        ):
            return
        for attribute in ("thread_id", "scope_thread_id", "origin_thread_id"):
            thread_id = str(getattr(file_row, attribute, "") or "").strip()
            if thread_id and deps.check_thread_member(db, org, thread_id, user_id):
                return
        raise HTTPException(status_code=403, detail="file_access_denied")

    @router.get("/api/documents/thread-context")
    def get_thread_document_context(
        thread_id: str,
        file_id: Optional[str] = None,
        query: Optional[str] = None,
        strict_file_id: bool = False,
        x_org_slug: Optional[str] = Header(default=None),
        user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(get_db),
    ) -> Dict[str, Any]:
        org = deps.get_request_org(user, x_org_slug)
        normalized_thread_id = str(thread_id or "").strip()
        if not normalized_thread_id:
            raise HTTPException(status_code=400, detail="thread_id_required")

        user_id = str(user.get("sub") or "")
        if user.get("role") != "admin":
            deps.require_thread_member(db, org, normalized_thread_id, user_id)

        try:
            context = build_thread_document_context(
                db,
                org=org,
                thread_id=normalized_thread_id,
                query=(query or "documento anexado"),
                top_k=8,
                preferred_file_id=(file_id or None),
                strict_preferred_file_id=bool(strict_file_id or file_id),
            )
            context.setdefault("diagnostic", {})
            context["diagnostic"]["write_executed"] = False
            deps.logger.info(
                "DOCIO_READONLY_CONTEXT_READY thread_id=%s file_id=%s evidence_count=%s",
                normalized_thread_id,
                file_id,
                int(context.get("file_evidence_count") or 0),
            )
            return context
        except HTTPException:
            raise
        except Exception as exc:
            try:
                db.rollback()
            except Exception:
                pass
            deps.logger.exception(
                "DOCIO_READONLY_CONTEXT_FAILED thread_id=%s file_id=%s",
                normalized_thread_id,
                file_id,
            )
            raise HTTPException(
                status_code=500,
                detail=f"document_context_failed:{exc.__class__.__name__}",
            ) from exc

    @router.get("/api/files/{file_id}/download")
    def download_file(
        file_id: str,
        x_org_slug: Optional[str] = Header(default=None),
        user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(get_db),
    ) -> Response:
        org = deps.get_request_org(user, x_org_slug)
        file_row = db.get(File, file_id)
        if not file_row or str(getattr(file_row, "org_slug", "")) != org:
            raise HTTPException(status_code=404, detail="file_not_found")
        _require_file_read_access(db, org, file_row, user)

        raw = getattr(file_row, "content", None)
        if raw is None or len(raw) == 0:
            raise HTTPException(status_code=404, detail="file_content_not_available")

        filename = str(getattr(file_row, "filename", "") or "orkio_document")
        headers = {
            "Content-Disposition": _content_disposition(filename),
            "Cache-Control": "private, no-store",
            "Pragma": "no-cache",
            "X-Content-Type-Options": "nosniff",
        }
        return Response(
            content=bytes(raw),
            media_type=(
                getattr(file_row, "mime_type", None)
                or "application/octet-stream"
            ),
            headers=headers,
        )

    @router.post("/api/document-artifacts/generate")
    async def generate_document_artifact_endpoint(
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(get_db),
    ) -> Dict[str, Any]:
        started = time.monotonic()
        request_id = _request_id(request)
        path = "/api/document-artifacts/generate"
        org = deps.get_request_org(user, x_org_slug)
        user_id = str(user.get("sub") or "")
        limits = DocumentArtifactLimits.from_env()

        try:
            payload = await _read_limited_json_body(
                request,
                max_bytes=limits.max_request_bytes,
            )
            try:
                input_model = DocumentArtifactGenerateIn.model_validate(payload)
            except ValidationError as exc:
                raise HTTPException(
                    status_code=422,
                    detail=exc.errors(include_url=False),
                ) from exc

            thread_id = str(input_model.thread_id or "").strip() or None
            if thread_id:
                if user.get("role") != "admin":
                    deps.require_thread_member(db, org, thread_id, user_id)
                thread = db.execute(
                    select(Thread).where(
                        Thread.org_slug == org,
                        Thread.id == thread_id,
                    )
                ).scalar_one_or_none()
                if thread is None:
                    raise HTTPException(status_code=404, detail="thread_not_found")

            command_deps = DocumentArtifactCommandDeps(
                new_id=deps.new_id,
                now_ts=deps.now_ts,
                logger=deps.logger,
                generate_artifact=generate_document_artifact_isolated,
                stage_audit_record=stage_audit,
            )

            def _run_command() -> Dict[str, Any]:
                command_db = deps.session_factory()
                try:
                    return execute_document_artifact_command(
                        command_db,
                        input_model=input_model,
                        org=org,
                        user=user,
                        request_id=request_id,
                        path=path,
                        deps=command_deps,
                        limits=limits,
                        resolved_agent_id=None,
                        resolved_agent_name=None,
                        assistant_text_builder=None,
                        authorship_claim="user_or_system",
                    )
                finally:
                    command_db.close()

            return await asyncio.to_thread(_run_command)

        except HTTPException as exc:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.generate.rejected",
                request_id=request_id,
                path=path,
                status_code=exc.status_code,
                started=started,
                detail=str(exc.detail),
            )
            raise
        except DocumentArtifactThreadNotFound as exc:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.generate.rejected",
                request_id=request_id,
                path=path,
                status_code=404,
                started=started,
                detail=str(exc),
            )
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except DocumentArtifactLimitError as exc:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.generate.rejected",
                request_id=request_id,
                path=path,
                status_code=413,
                started=started,
                detail=str(exc),
            )
            raise HTTPException(status_code=413, detail=str(exc)) from exc
        except DocumentArtifactTimeoutError as exc:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.generate.timeout",
                request_id=request_id,
                path=path,
                status_code=408,
                started=started,
                detail=str(exc),
            )
            raise HTTPException(status_code=408, detail=str(exc)) from exc
        except (DocioLockUnavailable, DocioQuotaExceeded) as exc:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.generate.rate_limited",
                request_id=request_id,
                path=path,
                status_code=429,
                started=started,
                detail=str(exc),
            )
            raise HTTPException(status_code=429, detail=str(exc)) from exc
        except DocioCoordinationUnavailable as exc:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.generate.coordination_failed",
                request_id=request_id,
                path=path,
                status_code=503,
                started=started,
                detail=str(exc),
            )
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except DocumentArtifactConcurrencyError as exc:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.generate.concurrency_limited",
                request_id=request_id,
                path=path,
                status_code=429,
                started=started,
                detail=str(exc),
            )
            raise HTTPException(status_code=429, detail=str(exc)) from exc
        except DocumentArtifactWorkerError as exc:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.generate.failed",
                request_id=request_id,
                path=path,
                status_code=501,
                started=started,
                detail=str(exc),
            )
            raise HTTPException(status_code=501, detail=str(exc)) from exc
        except Exception as exc:
            try:
                db.rollback()
            except Exception:
                pass
            deps.logger.exception(
                "DOCIO_GENERATION_FAILED org=%s user_id=%s request_id=%s",
                org,
                user_id,
                request_id,
            )
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.generate.failed",
                request_id=request_id,
                path=path,
                status_code=503,
                started=started,
                detail=exc.__class__.__name__,
            )
            raise HTTPException(
                status_code=503,
                detail="document_generation_transaction_failed",
            ) from exc

    @router.post("/api/files/{file_id}/reindex")
    def reindex_file(
        file_id: str,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        user: Dict[str, Any] = Depends(deps.get_current_user),
        db: Session = Depends(get_db),
    ) -> Dict[str, Any]:
        started = time.monotonic()
        request_id = _request_id(request)
        path = f"/api/files/{file_id}/reindex"
        org = deps.get_request_org(user, x_org_slug)
        user_id = str(user.get("sub") or "")

        if user.get("role") != "admin":
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.reindex.rejected",
                request_id=request_id,
                path=path,
                status_code=403,
                started=started,
                detail="admin_required",
            )
            raise HTTPException(status_code=403, detail="admin_required")

        file_row = db.get(File, file_id)
        if not file_row or str(getattr(file_row, "org_slug", "")) != org:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.reindex.rejected",
                request_id=request_id,
                path=path,
                status_code=404,
                started=started,
                detail="file_not_found",
            )
            raise HTTPException(status_code=404, detail="file_not_found")

        try:
            with distributed_locks(
                db,
                (("docio_reindex_file", f"{org}:{file_id}"),),
            ):
                now = deps.now_ts()
                last_success = last_successful_reindex_at(
                    db,
                    org=org,
                    file_id=file_id,
                )
                minimum_interval = _bounded_reindex_interval()
                if last_success is not None and now - last_success < minimum_interval:
                    raise DocioQuotaExceeded("reindex_rate_limited")

                index_result = stage_binary_reindex(
                    db,
                    file_row=file_row,
                    now_ts=now,
                )
                stage_audit(
                    db,
                    audit_id=deps.new_id(),
                    org=org,
                    user_id=user_id,
                    action="document_artifact.reindex.completed",
                    request_id=request_id,
                    path=path,
                    status_code=200,
                    latency_ms=_latency_ms(started),
                    now_ts=now,
                    meta={
                        "file_id": file_id,
                        "filename": file_row.filename,
                        "extracted_chars": int(
                            index_result.get("extracted_chars") or 0
                        ),
                        "chunks_created": int(
                            index_result.get("chunks_created") or 0
                        ),
                        "write_executed": True,
                    },
                )
                db.commit()

            return {
                "ok": True,
                "file_id": file_id,
                "extracted_chars": int(index_result.get("extracted_chars") or 0),
                "chunks_created": int(index_result.get("chunks_created") or 0),
                "audit_persisted": True,
                "write_executed": True,
            }
        except DocioLockUnavailable as exc:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.reindex.locked",
                request_id=request_id,
                path=path,
                status_code=409,
                started=started,
                detail=str(exc),
            )
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except DocioQuotaExceeded as exc:
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.reindex.rate_limited",
                request_id=request_id,
                path=path,
                status_code=429,
                started=started,
                detail=str(exc),
            )
            raise HTTPException(status_code=429, detail=str(exc)) from exc
        except (DocioCoordinationUnavailable, DocioReindexError) as exc:
            status_code = 503 if isinstance(exc, DocioCoordinationUnavailable) else 422
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.reindex.failed",
                request_id=request_id,
                path=path,
                status_code=status_code,
                started=started,
                detail=str(exc),
            )
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        except Exception as exc:
            try:
                db.rollback()
            except Exception:
                pass
            deps.logger.exception(
                "DOCIO_REINDEX_FAILED org=%s file_id=%s request_id=%s",
                org,
                file_id,
                request_id,
            )
            _persist_failure_or_raise(
                db,
                org=org,
                user_id=user_id,
                action="document_artifact.reindex.failed",
                request_id=request_id,
                path=path,
                status_code=503,
                started=started,
                detail=exc.__class__.__name__,
            )
            raise HTTPException(
                status_code=503,
                detail="document_reindex_transaction_failed",
            ) from exc

    return router
