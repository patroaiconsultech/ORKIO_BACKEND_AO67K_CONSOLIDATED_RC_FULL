"""MCP server entrypoint for Orkio Auditor Readonly Fase 1."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import tools


mcp = FastMCP("orkio-auditor-readonly")


@mcp.tool(name="get_health")
def get_health() -> dict:
    """Return sanitized health and readonly connectivity metadata."""
    return tools.get_health()


@mcp.tool(name="get_recent_logs_sanitized")
def get_recent_logs_sanitized(limit: int | None = None, severity: str | None = None) -> dict:
    """Return sanitized recent logs from configured local log files."""
    return tools.get_recent_logs_sanitized(limit=limit, severity=severity)


@mcp.tool(name="get_thread_metadata")
def get_thread_metadata(thread_id: str, org_id: str | None = None) -> dict:
    """Return metadata for one thread without message bodies."""
    return tools.get_thread_metadata(thread_id=thread_id, org_id=org_id)


@mcp.tool(name="get_message_counts")
def get_message_counts(thread_id: str, org_id: str | None = None) -> dict:
    """Return message counts for a thread without message content."""
    return tools.get_message_counts(thread_id=thread_id, org_id=org_id)


@mcp.tool(name="get_file_refs")
def get_file_refs(thread_id: str, org_id: str | None = None, limit: int | None = None) -> dict:
    """Return file references for a thread without file contents."""
    return tools.get_file_refs(thread_id=thread_id, org_id=org_id, limit=limit)


@mcp.tool(name="get_runtime_flags")
def get_runtime_flags() -> dict:
    """Return non-sensitive runtime flag presence and boolean allowlist values."""
    return tools.get_runtime_flags()


@mcp.tool(name="get_audit_reports")
def get_audit_reports(limit: int | None = None) -> dict:
    """Return audit report metadata without full report contents."""
    return tools.get_audit_reports(limit=limit)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
