from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, Optional, Sequence, Tuple

from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from ..models import AuditLog, File, FileChunk, FileText
from .file_upload_indexing_service import extract_text_with_fallback


class DocioGovernanceError(Exception):
    """Base DOCIO governance error."""


class DocioLockUnavailable(DocioGovernanceError):
    """A distributed DOCIO operation is already running."""


class DocioCoordinationUnavailable(DocioGovernanceError):
    """The active database cannot provide safe coordination."""


class DocioQuotaExceeded(DocioGovernanceError):
    """A prospective count or byte quota would be exceeded."""


class DocioAuditPersistenceError(DocioGovernanceError):
    """An operation could not prove its audit trail."""


class DocioReindexError(DocioGovernanceError):
    """A reindex operation could not produce valid text."""


@dataclass(frozen=True)
class DocioQuotaPolicy:
    user_count_per_hour: int = 30
    tenant_count_per_hour: int = 300
    user_bytes_per_hour: int = 50 * 1024 * 1024
    tenant_bytes_per_hour: int = 500 * 1024 * 1024
    tenant_bytes_per_month: int = 5 * 1024 * 1024 * 1024

    @classmethod
    def from_env(cls) -> "DocioQuotaPolicy":
        return cls(
            user_count_per_hour=_bounded_int(
                "ORKIO_DOCIO_USER_COUNT_PER_HOUR", 30, 1, 1_000
            ),
            tenant_count_per_hour=_bounded_int(
                "ORKIO_DOCIO_TENANT_COUNT_PER_HOUR", 300, 1, 10_000
            ),
            user_bytes_per_hour=_bounded_int(
                "ORKIO_DOCIO_USER_BYTES_PER_HOUR",
                50 * 1024 * 1024,
                1 * 1024 * 1024,
                10 * 1024 * 1024 * 1024,
            ),
            tenant_bytes_per_hour=_bounded_int(
                "ORKIO_DOCIO_TENANT_BYTES_PER_HOUR",
                500 * 1024 * 1024,
                1 * 1024 * 1024,
                100 * 1024 * 1024 * 1024,
            ),
            tenant_bytes_per_month=_bounded_int(
                "ORKIO_DOCIO_TENANT_BYTES_PER_MONTH",
                5 * 1024 * 1024 * 1024,
                1 * 1024 * 1024,
                1024 * 1024 * 1024 * 1024,
            ),
        )


@dataclass(frozen=True)
class DocioQuotaSnapshot:
    user_count_hour: int
    user_bytes_hour: int
    tenant_count_hour: int
    tenant_bytes_hour: int
    tenant_bytes_month: int

    def as_dict(self) -> Dict[str, int]:
        return {
            "user_count_hour": self.user_count_hour,
            "user_bytes_hour": self.user_bytes_hour,
            "tenant_count_hour": self.tenant_count_hour,
            "tenant_bytes_hour": self.tenant_bytes_hour,
            "tenant_bytes_month": self.tenant_bytes_month,
        }


_LOCAL_LOCKS: Dict[int, threading.Lock] = {}
_LOCAL_LOCKS_GUARD = threading.Lock()


def _bounded_int(name: str, default: int, minimum: int, maximum: int) -> int:
    raw = os.getenv(name)
    try:
        value = int(raw) if raw not in (None, "") else int(default)
    except (TypeError, ValueError):
        value = int(default)
    return max(minimum, min(value, maximum))


def _advisory_key(namespace: str, value: str) -> int:
    digest = hashlib.sha256(f"{namespace}:{value}".encode("utf-8")).digest()
    unsigned = int.from_bytes(digest[:8], "big", signed=False)
    # PostgreSQL advisory locks use a signed BIGINT.
    return unsigned if unsigned < (1 << 63) else unsigned - (1 << 64)


def _local_lock(key: int) -> threading.Lock:
    with _LOCAL_LOCKS_GUARD:
        return _LOCAL_LOCKS.setdefault(key, threading.Lock())


@contextmanager
def distributed_lock(
    db: Session,
    *,
    namespace: str,
    value: str,
) -> Iterator[None]:
    """Acquire a cross-replica lock on PostgreSQL.

    SQLite is supported only as a deterministic local substitute for tests.
    Any other dialect fails closed instead of silently degrading to memory.
    """

    bind = db.get_bind()
    dialect = str(getattr(getattr(bind, "dialect", None), "name", "") or "")
    key = _advisory_key(namespace, value)

    if dialect == "postgresql":
        # Session.get_bind() may return either an Engine or an already-bound
        # Connection. Advisory locks must use a dedicated connection so the
        # lock lifetime is independent from the caller transaction.
        connection_factory = getattr(bind, "engine", bind)
        connection = connection_factory.connect()
        acquired = False
        try:
            acquired = bool(
                connection.execute(
                    text("SELECT pg_try_advisory_lock(:lock_key)"),
                    {"lock_key": key},
                ).scalar()
            )
            if not acquired:
                raise DocioLockUnavailable(f"{namespace}_lock_busy")
            yield
        finally:
            if acquired:
                try:
                    connection.execute(
                        text("SELECT pg_advisory_unlock(:lock_key)"),
                        {"lock_key": key},
                    )
                except Exception:
                    pass
            try:
                connection.rollback()
            except Exception:
                pass
            connection.close()
        return

    if dialect == "sqlite":
        lock = _local_lock(key)
        if not lock.acquire(blocking=False):
            raise DocioLockUnavailable(f"{namespace}_lock_busy")
        try:
            yield
        finally:
            lock.release()
        return

    raise DocioCoordinationUnavailable(
        f"distributed_coordination_requires_postgresql:{dialect or 'unknown'}"
    )


@contextmanager
def distributed_locks(
    db: Session,
    locks: Sequence[Tuple[str, str]],
) -> Iterator[None]:
    """Acquire several locks in a stable order to avoid deadlocks."""

    ordered = sorted(
        {(str(namespace), str(value)) for namespace, value in locks},
        key=lambda item: (_advisory_key(item[0], item[1]), item[0], item[1]),
    )
    with ExitStack() as stack:
        for namespace, value in ordered:
            stack.enter_context(
                distributed_lock(db, namespace=namespace, value=value)
            )
        yield


def quota_snapshot(
    db: Session,
    *,
    org: str,
    user_id: str,
    now_ts: int,
) -> DocioQuotaSnapshot:
    hour_start = int(now_ts) - 3600
    month_start = int(now_ts) - (31 * 24 * 3600)

    user_count, user_bytes = db.execute(
        select(
            func.count(File.id),
            func.coalesce(func.sum(File.size_bytes), 0),
        ).where(
            File.org_slug == org,
            File.origin == "generated",
            File.uploader_id == user_id,
            File.created_at >= hour_start,
        )
    ).one()

    tenant_count, tenant_bytes = db.execute(
        select(
            func.count(File.id),
            func.coalesce(func.sum(File.size_bytes), 0),
        ).where(
            File.org_slug == org,
            File.origin == "generated",
            File.created_at >= hour_start,
        )
    ).one()

    tenant_month_bytes = db.execute(
        select(func.coalesce(func.sum(File.size_bytes), 0)).where(
            File.org_slug == org,
            File.origin == "generated",
            File.created_at >= month_start,
        )
    ).scalar_one()

    return DocioQuotaSnapshot(
        user_count_hour=int(user_count or 0),
        user_bytes_hour=int(user_bytes or 0),
        tenant_count_hour=int(tenant_count or 0),
        tenant_bytes_hour=int(tenant_bytes or 0),
        tenant_bytes_month=int(tenant_month_bytes or 0),
    )


def enforce_prospective_quota(
    db: Session,
    *,
    org: str,
    user_id: str,
    prospective_bytes: int,
    now_ts: int,
    policy: Optional[DocioQuotaPolicy] = None,
) -> DocioQuotaSnapshot:
    trusted = policy or DocioQuotaPolicy.from_env()
    prospective = max(0, int(prospective_bytes))
    snapshot = quota_snapshot(db, org=org, user_id=user_id, now_ts=now_ts)

    checks = (
        (
            snapshot.user_count_hour + 1,
            trusted.user_count_per_hour,
            "user_count_hour_quota_exceeded",
        ),
        (
            snapshot.tenant_count_hour + 1,
            trusted.tenant_count_per_hour,
            "tenant_count_hour_quota_exceeded",
        ),
        (
            snapshot.user_bytes_hour + prospective,
            trusted.user_bytes_per_hour,
            "user_bytes_hour_quota_exceeded",
        ),
        (
            snapshot.tenant_bytes_hour + prospective,
            trusted.tenant_bytes_per_hour,
            "tenant_bytes_hour_quota_exceeded",
        ),
        (
            snapshot.tenant_bytes_month + prospective,
            trusted.tenant_bytes_per_month,
            "tenant_bytes_month_quota_exceeded",
        ),
    )
    for projected, limit, error in checks:
        if projected > limit:
            raise DocioQuotaExceeded(error)
    return snapshot


def stage_text_index(
    db: Session,
    *,
    org: str,
    file_id: str,
    text_content: str,
    now_ts: int,
) -> Dict[str, Any]:
    """Stage FileText/FileChunk rows without committing.

    The caller owns the transaction, so file, index, thread event and audit can
    become visible atomically.
    """

    normalized = str(text_content or "").replace("\x00", " ").strip()
    db.execute(
        delete(FileText).where(
            FileText.org_slug == org,
            FileText.file_id == file_id,
        )
    )
    db.execute(
        delete(FileChunk).where(
            FileChunk.org_slug == org,
            FileChunk.file_id == file_id,
        )
    )

    if not normalized:
        return {
            "text": "",
            "extracted_chars": 0,
            "chunks_created": 0,
            "has_extracted_text": False,
        }

    db.add(
        FileText(
            id=_random_id(),
            org_slug=org,
            file_id=file_id,
            text=normalized,
            extracted_chars=len(normalized),
            created_at=int(now_ts),
        )
    )

    chunk_chars = _bounded_int("RAG_CHUNK_CHARS", 1_200, 400, 4_000)
    overlap = _bounded_int(
        "RAG_CHUNK_OVERLAP",
        200,
        0,
        max(0, int(chunk_chars * 0.6)),
    )
    position = 0
    index = 0
    chunks_created = 0
    while position < len(normalized):
        end = min(len(normalized), position + chunk_chars)
        chunk = normalized[position:end].strip()
        if chunk:
            db.add(
                FileChunk(
                    id=_random_id(),
                    org_slug=org,
                    file_id=file_id,
                    idx=index,
                    content=chunk,
                    created_at=int(now_ts),
                )
            )
            index += 1
            chunks_created += 1
        if end >= len(normalized):
            break
        position = max(0, end - overlap)

    return {
        "text": normalized,
        "extracted_chars": len(normalized),
        "chunks_created": chunks_created,
        "has_extracted_text": True,
    }


def stage_binary_reindex(
    db: Session,
    *,
    file_row: File,
    now_ts: int,
) -> Dict[str, Any]:
    raw = bytes(getattr(file_row, "content", None) or b"")
    if not raw:
        raise DocioReindexError("file_content_not_available")

    text_content, extracted_chars, diagnostics = extract_text_with_fallback(
        str(getattr(file_row, "filename", "") or "document"),
        raw,
        getattr(file_row, "mime_type", None),
    )
    if not str(text_content or "").strip():
        raise DocioReindexError("document_text_extraction_empty")

    result = stage_text_index(
        db,
        org=str(file_row.org_slug),
        file_id=str(file_row.id),
        text_content=text_content,
        now_ts=int(now_ts),
    )
    file_row.extraction_failed = False
    db.add(file_row)
    result["diagnostics"] = diagnostics
    result["extracted_chars"] = int(extracted_chars or result["extracted_chars"])
    return result


def stage_audit(
    db: Session,
    *,
    audit_id: str,
    org: str,
    user_id: Optional[str],
    action: str,
    request_id: str,
    path: str,
    status_code: int,
    latency_ms: int,
    now_ts: int,
    meta: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    row = AuditLog(
        id=audit_id,
        org_slug=org,
        user_id=user_id,
        action=action,
        meta=json.dumps(meta or {}, ensure_ascii=False, sort_keys=True),
        request_id=request_id,
        path=path,
        status_code=int(status_code),
        latency_ms=max(0, int(latency_ms)),
        created_at=int(now_ts),
    )
    db.add(row)
    return row


def commit_failure_audit(
    db: Session,
    *,
    audit_id: str,
    org: str,
    user_id: Optional[str],
    action: str,
    request_id: str,
    path: str,
    status_code: int,
    latency_ms: int,
    now_ts: int,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """Persist a failure audit in its own transaction or fail explicitly."""

    try:
        db.rollback()
        stage_audit(
            db,
            audit_id=audit_id,
            org=org,
            user_id=user_id,
            action=action,
            request_id=request_id,
            path=path,
            status_code=status_code,
            latency_ms=latency_ms,
            now_ts=now_ts,
            meta=meta,
        )
        db.commit()
    except Exception as exc:
        try:
            db.rollback()
        except Exception:
            pass
        raise DocioAuditPersistenceError("audit_persistence_failed") from exc


def last_successful_reindex_at(
    db: Session,
    *,
    org: str,
    file_id: str,
) -> Optional[int]:
    value = db.execute(
        select(func.max(AuditLog.created_at)).where(
            AuditLog.org_slug == org,
            AuditLog.action == "document_artifact.reindex.completed",
            AuditLog.path == f"/api/files/{file_id}/reindex",
            AuditLog.status_code == 200,
        )
    ).scalar_one()
    return int(value) if value is not None else None


def _random_id() -> str:
    import uuid

    return uuid.uuid4().hex
