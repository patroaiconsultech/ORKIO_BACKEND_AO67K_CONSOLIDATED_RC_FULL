from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import File, Message, Thread
from ..schemas.document_artifacts import DocumentArtifactGenerateIn
from .document_artifact_service import (
    DocumentArtifactLimits,
    GeneratedDocumentArtifact,
    generate_document_artifact_isolated,
)
from .document_governance_service import (
    distributed_locks,
    enforce_prospective_quota,
    stage_audit,
    stage_text_index,
)


class DocumentArtifactThreadNotFound(LookupError):
    """The requested thread does not exist in the active tenant."""


@dataclass(frozen=True)
class DocumentArtifactCommandDeps:
    new_id: Callable[[], str]
    now_ts: Callable[[], int]
    logger: logging.Logger
    generate_artifact: Callable[..., GeneratedDocumentArtifact] = (
        generate_document_artifact_isolated
    )
    stage_audit_record: Callable[..., Any] = stage_audit


def execute_document_artifact_command(
    db: Session,
    *,
    input_model: DocumentArtifactGenerateIn,
    org: str,
    user: Dict[str, Any],
    request_id: str,
    path: str,
    deps: DocumentArtifactCommandDeps,
    limits: Optional[DocumentArtifactLimits] = None,
    resolved_agent_id: Optional[str] = None,
    resolved_agent_name: Optional[str] = None,
    assistant_text_builder: Optional[Callable[[Dict[str, Any]], str]] = None,
    authorship_claim: str = "user_or_system",
) -> Dict[str, Any]:
    """Generate, persist, index and audit one artifact in a single transaction.

    Authorization is owned by the caller. This command validates tenant/thread
    existence and preserves atomic truth for File, index, thread event, optional
    assistant message and AuditLog.
    """

    trusted_limits = limits or DocumentArtifactLimits.from_env()
    org_slug = str(org or "").strip()
    user_id = str(user.get("sub") or "").strip()
    thread_id = str(input_model.thread_id or "").strip() or None
    agent_id = str(resolved_agent_id or "").strip() or None
    agent_name = str(resolved_agent_name or "").strip() or None
    execution_id = deps.new_id()

    try:
        if thread_id:
            thread = db.execute(
                select(Thread).where(
                    Thread.org_slug == org_slug,
                    Thread.id == thread_id,
                )
            ).scalar_one_or_none()
            if thread is None:
                raise DocumentArtifactThreadNotFound("thread_not_found")

        locks = (
            ("docio_generation_tenant", org_slug),
            ("docio_generation_user", f"{org_slug}:{user_id}"),
        )
        with distributed_locks(db, locks):
            enforce_prospective_quota(
                db,
                org=org_slug,
                user_id=user_id,
                prospective_bytes=0,
                now_ts=deps.now_ts(),
            )

            artifact = deps.generate_artifact(
                input_model.model_dump(),
                limits=trusted_limits,
            )

            now = deps.now_ts()
            quota_before = enforce_prospective_quota(
                db,
                org=org_slug,
                user_id=user_id,
                prospective_bytes=len(artifact.content),
                now_ts=now,
            )

            file_id = deps.new_id()
            file_row = File(
                id=file_id,
                org_slug=org_slug,
                thread_id=thread_id,
                uploader_id=user_id,
                uploader_name=user.get("name"),
                uploader_email=user.get("email"),
                filename=artifact.filename,
                original_filename=artifact.filename,
                origin="generated",
                scope_thread_id=thread_id,
                scope_agent_id=agent_id,
                mime_type=artifact.mime_type,
                size_bytes=len(artifact.content),
                content=artifact.content,
                extraction_failed=False,
                is_institutional=False,
                created_at=now,
            )
            db.add(file_row)

            index_result = stage_text_index(
                db,
                org=org_slug,
                file_id=file_id,
                text_content=artifact.text_content,
                now_ts=now,
            )
            file_row.extraction_failed = not bool(
                index_result.get("has_extracted_text")
            )
            db.add(file_row)

            artifact_meta = {
                "kind": "document_artifact",
                "type": "generated_file",
                "capability": "document_artifact_generate",
                "file_id": file_id,
                "filename": artifact.filename,
                "format": artifact.format,
                "mime_type": artifact.mime_type,
                "mime": artifact.mime_type,
                "size_bytes": len(artifact.content),
                "size": len(artifact.content),
                "thread_id": thread_id,
                "download_url": f"/api/files/{file_id}/download",
                "created_by_user_id": user_id,
                "created_by_user_name": user.get("name"),
                "requested_agent_hint": input_model.requested_agent_hint,
                "resolved_agent_id": agent_id,
                "resolved_agent": agent_name,
                "execution_id": execution_id,
                "authorship_claim": authorship_claim,
                "write_kind": "user_requested_artifact",
                "human_approval_required": False,
                "ts": now,
            }

            event_persisted = False
            if thread_id:
                visible_text = f"📄 Artefato gerado: {artifact.filename}"
                event_payload = {
                    **artifact_meta,
                    "text": visible_text,
                }
                db.add(
                    Message(
                        id=deps.new_id(),
                        org_slug=org_slug,
                        thread_id=thread_id,
                        user_id=user_id,
                        user_name=user.get("name"),
                        role="system",
                        agent_id=agent_id,
                        agent_name=agent_name,
                        content=(
                            visible_text
                            + "\n\nORKIO_EVENT:"
                            + json.dumps(event_payload, ensure_ascii=False)
                        ),
                        created_at=now,
                    )
                )
                event_persisted = True

            assistant_message_id = None
            assistant_text = None
            if thread_id and assistant_text_builder is not None:
                assistant_text = str(assistant_text_builder(dict(artifact_meta)) or "").strip()
                if assistant_text:
                    assistant_message_id = deps.new_id()
                    db.add(
                        Message(
                            id=assistant_message_id,
                            org_slug=org_slug,
                            thread_id=thread_id,
                            role="assistant",
                            content=assistant_text,
                            agent_id=agent_id,
                            agent_name=agent_name,
                            created_at=now,
                        )
                    )

            audit_meta = {
                **artifact_meta,
                "extracted_chars": int(index_result.get("extracted_chars") or 0),
                "chunks_created": int(index_result.get("chunks_created") or 0),
                "thread_event_persisted": event_persisted,
                "assistant_message_id": assistant_message_id,
                "quota_before": quota_before.as_dict(),
            }
            deps.stage_audit_record(
                db,
                audit_id=deps.new_id(),
                org=org_slug,
                user_id=user_id,
                action="document_artifact.generated",
                request_id=request_id,
                path=path,
                status_code=200,
                latency_ms=0,
                now_ts=now,
                meta=audit_meta,
            )

            db.commit()

        result = {
            "ok": True,
            "file_id": file_id,
            "filename": artifact.filename,
            "format": artifact.format,
            "mime_type": artifact.mime_type,
            "size_bytes": len(artifact.content),
            "thread_id": thread_id,
            "download_url": f"/api/files/{file_id}/download",
            "extracted_chars": int(index_result.get("extracted_chars") or 0),
            "chunks_created": int(index_result.get("chunks_created") or 0),
            "extraction_failed": bool(file_row.extraction_failed),
            "thread_event_persisted": event_persisted,
            "audit_persisted": True,
            "execution_id": execution_id,
            "resolved_agent_id": agent_id,
            "resolved_agent": agent_name,
            "authorship_claim": authorship_claim,
            "assistant_persisted": bool(assistant_message_id),
            "assistant_message_id": assistant_message_id,
            "assistant_text": assistant_text,
            "artifact": dict(artifact_meta),
            "artifacts": [dict(artifact_meta)],
        }
        return result
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        raise
