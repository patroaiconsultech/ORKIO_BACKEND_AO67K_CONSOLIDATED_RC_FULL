"""RBAC enforcement for readonly MCP Auditor tools."""

from __future__ import annotations

from .auth import AuditorPrincipal


class AuditorPermissionError(PermissionError):
    """Raised when a principal is not allowed to call a tool or org scope."""


READONLY_TOOLS = frozenset(
    {
        "get_health",
        "get_recent_logs_sanitized",
        "get_thread_metadata",
        "get_message_counts",
        "get_file_refs",
        "get_runtime_flags",
        "get_audit_reports",
    }
)


def authorize_tool(principal: AuditorPrincipal, tool_name: str, org_id: str | None = None) -> None:
    if not principal.is_readonly_auditor:
        raise AuditorPermissionError("principal is not readonly auditor")
    if tool_name not in READONLY_TOOLS:
        raise AuditorPermissionError("tool is not readonly")
    if tool_name not in principal.allowed_tools:
        raise AuditorPermissionError("tool not allowed")
    if "*" in principal.allowed_org_ids:
        return
    if org_id is None:
        return
    if str(org_id) not in principal.allowed_org_ids:
        raise AuditorPermissionError("organization not allowed")
