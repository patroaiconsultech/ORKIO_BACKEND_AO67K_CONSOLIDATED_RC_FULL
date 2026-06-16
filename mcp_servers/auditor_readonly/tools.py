"""Readonly MCP tool implementations."""

from __future__ import annotations

from typing import Any, Callable

from .audit_trail import append_audit_event, new_correlation_id
from .auth import AuditorPrincipal, principal_from_config
from .queries import (
    fetch_file_refs,
    fetch_message_counts,
    fetch_thread_metadata,
    get_health_snapshot,
    list_audit_reports,
    read_recent_logs_sanitized,
    read_runtime_flags,
)
from .rbac import authorize_tool
from .sanitizers import hash_identifier, safe_error


def _execute_tool(tool_name: str, org_id: str | None, resource_refs: dict[str, Any], handler: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    correlation_id = new_correlation_id()
    principal: AuditorPrincipal | None = None
    try:
        principal = principal_from_config()
        authorize_tool(principal, tool_name, org_id=org_id)
        append_audit_event(
            correlation_id=correlation_id,
            principal=principal,
            tool_name=tool_name,
            outcome="started",
            resource_refs=resource_refs,
        )
        payload = handler(correlation_id)
        append_audit_event(
            correlation_id=correlation_id,
            principal=principal,
            tool_name=tool_name,
            outcome="ok",
            resource_refs=resource_refs,
        )
        return payload
    except Exception as exc:
        append_audit_event(
            correlation_id=correlation_id,
            principal=principal,
            tool_name=tool_name,
            outcome="error",
            resource_refs=resource_refs,
            error=exc.__class__.__name__,
        )
        return {"ok": False, "tool": tool_name, "correlation_id": correlation_id, "error": safe_error(exc)}


def get_health() -> dict[str, Any]:
    tool_name = "get_health"

    def handler(correlation_id: str) -> dict[str, Any]:
        snapshot = get_health_snapshot()
        return {"ok": True, "tool": tool_name, "correlation_id": correlation_id, **snapshot}

    return _execute_tool(tool_name, None, {}, handler)


def get_recent_logs_sanitized(limit: int | None = None, severity: str | None = None) -> dict[str, Any]:
    tool_name = "get_recent_logs_sanitized"

    def handler(correlation_id: str) -> dict[str, Any]:
        payload = read_recent_logs_sanitized(limit=limit, severity=severity)
        return {"ok": True, "tool": tool_name, "correlation_id": correlation_id, **payload}

    return _execute_tool(tool_name, None, {"limit": limit, "severity": severity}, handler)


def get_thread_metadata(thread_id: str, org_id: str | None = None) -> dict[str, Any]:
    tool_name = "get_thread_metadata"

    def handler(correlation_id: str) -> dict[str, Any]:
        thread = fetch_thread_metadata(thread_id=thread_id, org_id=org_id)
        return {"ok": True, "tool": tool_name, "correlation_id": correlation_id, "thread": thread}

    return _execute_tool(tool_name, org_id, {"thread_id": thread_id, "org_id": org_id}, handler)


def get_message_counts(thread_id: str, org_id: str | None = None) -> dict[str, Any]:
    tool_name = "get_message_counts"

    def handler(correlation_id: str) -> dict[str, Any]:
        counts = fetch_message_counts(thread_id=thread_id, org_id=org_id)
        return {
            "ok": True,
            "tool": tool_name,
            "correlation_id": correlation_id,
            "thread_ref": hash_identifier(thread_id),
            "counts": counts,
        }

    return _execute_tool(tool_name, org_id, {"thread_id": thread_id, "org_id": org_id}, handler)


def get_file_refs(thread_id: str, org_id: str | None = None, limit: int | None = None) -> dict[str, Any]:
    tool_name = "get_file_refs"

    def handler(correlation_id: str) -> dict[str, Any]:
        files = fetch_file_refs(thread_id=thread_id, org_id=org_id, limit=limit)
        return {
            "ok": True,
            "tool": tool_name,
            "correlation_id": correlation_id,
            "thread_ref": hash_identifier(thread_id),
            "files": files,
        }

    return _execute_tool(tool_name, org_id, {"thread_id": thread_id, "org_id": org_id, "limit": limit}, handler)


def get_runtime_flags() -> dict[str, Any]:
    tool_name = "get_runtime_flags"

    def handler(correlation_id: str) -> dict[str, Any]:
        flags = read_runtime_flags()
        return {"ok": True, "tool": tool_name, "correlation_id": correlation_id, "flags": flags}

    return _execute_tool(tool_name, None, {}, handler)


def get_audit_reports(limit: int | None = None) -> dict[str, Any]:
    tool_name = "get_audit_reports"

    def handler(correlation_id: str) -> dict[str, Any]:
        reports = list_audit_reports(limit=limit)
        return {"ok": True, "tool": tool_name, "correlation_id": correlation_id, "reports": reports}

    return _execute_tool(tool_name, None, {"limit": limit}, handler)
