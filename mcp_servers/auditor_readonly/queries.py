"""Readonly data access for the Orkio MCP Auditor.

This module intentionally uses SQLAlchemy Core reflection and a strict column
allowlist. It must not select message bodies, extracted file text, embeddings,
passwords, tokens, cookies, secrets or raw payloads.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy import MetaData, Table, create_engine, func, select, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError

from .config import get_config
from .limits import clamp_limit
from .sanitizers import hash_identifier, runtime_value_for_public_flag, sanitize_filename, sanitize_text


THREAD_COLUMNS = ("id", "organization_id", "org_id", "user_id", "created_at", "updated_at", "last_message_at", "status", "archived", "title")
MESSAGE_COUNT_COLUMNS = ("id", "thread_id", "organization_id", "org_id", "role", "status", "created_at")
FILE_REF_COLUMNS = ("id", "thread_id", "organization_id", "org_id", "user_id", "filename", "name", "mime_type", "status", "size", "created_at", "updated_at")
AUDIT_REPORT_COLUMNS = ("id", "kind", "status", "created_at", "updated_at", "summary", "report_path")
FORBIDDEN_COLUMN_PARTS = (
    "content",
    "body",
    "text",
    "raw",
    "extract",
    "chunk",
    "embedding",
    "password",
    "token",
    "secret",
    "cookie",
)


class AuditorQueryError(RuntimeError):
    """Raised when readonly audit data cannot be collected safely."""


def _import_existing_engine() -> Engine | None:
    candidates = (
        ("app.db", "engine"),
        ("app.database", "engine"),
        ("src.db", "engine"),
        ("src.database", "engine"),
    )
    for module_name, attr_name in candidates:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            engine = getattr(module, attr_name, None)
        except Exception:
            continue
        if engine is not None:
            return engine
    return None


def get_engine() -> Engine:
    existing = _import_existing_engine()
    if existing is not None:
        return existing
    cfg = get_config()
    if not cfg.database_url:
        raise AuditorQueryError("readonly database URL is not configured")
    return create_engine(cfg.database_url, pool_pre_ping=True)


@contextmanager
def readonly_connection() -> Iterable[Connection]:
    engine = get_engine()
    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            if engine.dialect.name == "postgresql":
                conn.execute(text("SET TRANSACTION READ ONLY"))
            yield conn
            transaction.rollback()
        except Exception:
            transaction.rollback()
            raise


def _table(conn: Connection, table_name: str) -> Table:
    metadata = MetaData()
    try:
        return Table(table_name, metadata, autoload_with=conn)
    except SQLAlchemyError as exc:
        raise AuditorQueryError(f"table unavailable: {table_name}") from exc


def _safe_columns(table: Table, allowed: tuple[str, ...]) -> list[Any]:
    selected = []
    for name in allowed:
        if name in table.c and not any(part in name.lower() for part in FORBIDDEN_COLUMN_PARTS):
            selected.append(table.c[name])
    return selected


def _where_thread_org(table: Table, thread_id: str | None, org_id: str | None) -> list[Any]:
    clauses = []
    if thread_id is not None and "thread_id" in table.c:
        clauses.append(table.c.thread_id == thread_id)
    if thread_id is not None and "id" in table.c and "thread_id" not in table.c:
        clauses.append(table.c.id == thread_id)
    if org_id is not None:
        if "organization_id" in table.c:
            clauses.append(table.c.organization_id == org_id)
        elif "org_id" in table.c:
            clauses.append(table.c.org_id == org_id)
    return clauses


def _serialize_value(name: str, value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat() if value.tzinfo else value.replace(tzinfo=timezone.utc).isoformat()
    if name in {"user_id", "organization_id", "org_id"}:
        return hash_identifier(value)
    if name in {"title", "summary"}:
        return sanitize_text(value, max_chars=160)
    return value


def get_health_snapshot() -> dict[str, Any]:
    cfg = get_config()
    database = {"configured": bool(cfg.database_url), "connectivity": "not_checked", "pool": {}}
    try:
        with readonly_connection() as conn:
            conn.execute(text("SELECT 1"))
            database["connectivity"] = "ok"
            pool = getattr(conn.engine, "pool", None)
            if pool is not None:
                status = getattr(pool, "status", None)
                database["pool"] = {"status": sanitize_text(status(), max_chars=300) if callable(status) else "unavailable"}
    except Exception as exc:
        database["connectivity"] = "error"
        database["error"] = sanitize_text(exc.__class__.__name__, max_chars=120)
    return {
        "status": "ok" if database["connectivity"] in {"ok", "not_checked"} else "degraded",
        "database": database,
        "external_auth_required": cfg.external_auth_required,
        "enabled": cfg.enabled,
        "readonly": True,
    }


def read_recent_logs_sanitized(limit: int | None = None, severity: str | None = None) -> dict[str, Any]:
    cfg = get_config()
    effective_limit = clamp_limit(limit, min(50, cfg.max_log_lines), cfg.max_log_lines)
    if not cfg.log_paths:
        return {"source_configured": False, "lines": []}
    severity_filter = severity.lower() if severity else None
    collected: list[dict[str, Any]] = []
    for path in cfg.log_paths:
        if not path.exists() or not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for index, line in enumerate(lines[-effective_limit * 2 :], start=max(1, len(lines) - effective_limit * 2 + 1)):
            sanitized = sanitize_text(line, max_chars=1200)
            if severity_filter and severity_filter not in sanitized.lower():
                continue
            collected.append({"source_ref": hash_identifier(str(path.resolve())), "line": index, "message": sanitized})
    return {"source_configured": True, "lines": collected[-effective_limit:]}


def fetch_thread_metadata(thread_id: str, org_id: str | None = None) -> dict[str, Any] | None:
    cfg = get_config()
    with readonly_connection() as conn:
        table = _table(conn, cfg.table_names.threads)
        columns = _safe_columns(table, THREAD_COLUMNS)
        if not columns:
            raise AuditorQueryError("no safe thread metadata columns available")
        clauses = _where_thread_org(table, thread_id, org_id)
        stmt = select(*columns)
        for clause in clauses:
            stmt = stmt.where(clause)
        row = conn.execute(stmt.limit(1)).mappings().first()
        if row is None:
            return None
        result: dict[str, Any] = {}
        for key, value in row.items():
            if key == "id":
                result["thread_ref"] = hash_identifier(value)
            elif key == "title":
                result["title_ref"] = hash_identifier(value)
            else:
                result[key] = _serialize_value(key, value)
        return result


def fetch_message_counts(thread_id: str, org_id: str | None = None) -> dict[str, Any]:
    cfg = get_config()
    with readonly_connection() as conn:
        table = _table(conn, cfg.table_names.messages)
        clauses = _where_thread_org(table, thread_id, org_id)
        base = select(func.count()).select_from(table)
        for clause in clauses:
            base = base.where(clause)
        total = conn.execute(base).scalar_one()
        by_role: dict[str, int] = {}
        by_status: dict[str, int] = {}
        if "role" in table.c:
            stmt = select(table.c.role, func.count()).select_from(table)
            for clause in clauses:
                stmt = stmt.where(clause)
            stmt = stmt.group_by(table.c.role)
            by_role = {sanitize_text(str(role), max_chars=80): int(count) for role, count in conn.execute(stmt).all()}
        if "status" in table.c:
            stmt = select(table.c.status, func.count()).select_from(table)
            for clause in clauses:
                stmt = stmt.where(clause)
            stmt = stmt.group_by(table.c.status)
            by_status = {sanitize_text(str(status), max_chars=80): int(count) for status, count in conn.execute(stmt).all()}
        latest = None
        if "created_at" in table.c:
            stmt = select(func.max(table.c.created_at)).select_from(table)
            for clause in clauses:
                stmt = stmt.where(clause)
            latest = conn.execute(stmt).scalar_one_or_none()
        return {
            "thread_ref": hash_identifier(thread_id),
            "total": int(total),
            "by_role": by_role,
            "by_status": by_status,
            "latest_message_at": _serialize_value("latest_message_at", latest),
        }


def fetch_file_refs(thread_id: str, org_id: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    cfg = get_config()
    effective_limit = clamp_limit(limit, min(20, cfg.max_file_refs), cfg.max_file_refs)
    with readonly_connection() as conn:
        table = _table(conn, cfg.table_names.files)
        columns = _safe_columns(table, FILE_REF_COLUMNS)
        if not columns:
            raise AuditorQueryError("no safe file reference columns available")
        clauses = _where_thread_org(table, thread_id, org_id)
        stmt = select(*columns)
        for clause in clauses:
            stmt = stmt.where(clause)
        if "created_at" in table.c:
            stmt = stmt.order_by(table.c.created_at.desc())
        rows = conn.execute(stmt.limit(effective_limit)).mappings().all()
        files: list[dict[str, Any]] = []
        for row in rows:
            item: dict[str, Any] = {}
            for key, value in row.items():
                if key == "id":
                    item["file_ref"] = hash_identifier(value)
                elif key in {"filename", "name"}:
                    item.update(sanitize_filename(value))
                elif key in {"user_id", "organization_id", "org_id"}:
                    item[key] = hash_identifier(value)
                else:
                    item[key] = _serialize_value(key, value)
            files.append(item)
        return files


def read_runtime_flags() -> dict[str, str]:
    cfg = get_config()
    flags: dict[str, str] = {}
    prefixes = cfg.safe_runtime_prefixes
    for name, value in sorted(os.environ.items()):
        if len(flags) >= cfg.max_runtime_flags:
            break
        if not any(name.startswith(prefix) for prefix in prefixes):
            continue
        flags[name] = runtime_value_for_public_flag(name, value, cfg.public_flag_allowlist)
    return flags


def list_audit_reports(limit: int | None = None) -> list[dict[str, Any]]:
    cfg = get_config()
    effective_limit = clamp_limit(limit, min(20, cfg.max_audit_reports), cfg.max_audit_reports)
    reports_dir = Path(cfg.reports_dir)
    if not reports_dir.exists() or not reports_dir.is_dir():
        return []
    reports: list[dict[str, Any]] = []
    for path in sorted(reports_dir.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True)[:effective_limit]:
        try:
            stat = path.stat()
        except OSError:
            continue
        reports.append(
            {
                "report_ref": hash_identifier(path.name),
                "extension": path.suffix.lower(),
                "size_bytes": stat.st_size,
                "updated_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            }
        )
    return reports
