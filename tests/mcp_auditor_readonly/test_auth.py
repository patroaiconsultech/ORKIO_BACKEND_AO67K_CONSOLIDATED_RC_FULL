import pytest

from mcp_servers.auditor_readonly.auth import AuditorAuthError, principal_from_config
from mcp_servers.auditor_readonly.config import reload_config
from mcp_servers.auditor_readonly.rbac import AuditorPermissionError, authorize_tool


def configure_enabled(monkeypatch, allowed_org_ids="org-1", allowed_tools=None):
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ENABLED", "true")
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_EXTERNAL_AUTH_REQUIRED", "true")
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_PRINCIPAL_ID", "mcp_auditor_readonly")
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ROLE", "readonly_auditor")
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ALLOWED_ORG_IDS", allowed_org_ids)
    monkeypatch.setenv(
        "ORKIO_MCP_AUDITOR_ALLOWED_TOOLS",
        allowed_tools or "get_health,get_thread_metadata,get_message_counts,get_file_refs,get_runtime_flags,get_audit_reports,get_recent_logs_sanitized",
    )
    return reload_config()


def test_principal_requires_enabled(monkeypatch):
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ENABLED", "false")
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ALLOWED_ORG_IDS", "org-1")
    reload_config()

    with pytest.raises(AuditorAuthError):
        principal_from_config()


def test_principal_requires_readonly_role(monkeypatch):
    configure_enabled(monkeypatch)
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ROLE", "admin")
    reload_config()

    with pytest.raises(AuditorAuthError):
        principal_from_config()


def test_principal_requires_org_scope(monkeypatch):
    configure_enabled(monkeypatch)
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ALLOWED_ORG_IDS", "")
    reload_config()

    with pytest.raises(AuditorAuthError):
        principal_from_config()


def test_rbac_allows_readonly_tool_for_allowed_org(monkeypatch):
    configure_enabled(monkeypatch, allowed_org_ids="org-1")
    principal = principal_from_config()

    authorize_tool(principal, "get_thread_metadata", org_id="org-1")


def test_rbac_blocks_disallowed_org(monkeypatch):
    configure_enabled(monkeypatch, allowed_org_ids="org-1")
    principal = principal_from_config()

    with pytest.raises(AuditorPermissionError):
        authorize_tool(principal, "get_thread_metadata", org_id="org-2")


def test_rbac_blocks_non_readonly_tool(monkeypatch):
    configure_enabled(monkeypatch, allowed_org_ids="*")
    principal = principal_from_config()

    with pytest.raises(AuditorPermissionError):
        authorize_tool(principal, "apply_patch_to_branch", org_id="org-1")


def test_rbac_blocks_tool_not_in_allowlist(monkeypatch):
    configure_enabled(monkeypatch, allowed_org_ids="*", allowed_tools="get_health")
    principal = principal_from_config()

    with pytest.raises(AuditorPermissionError):
        authorize_tool(principal, "get_file_refs", org_id="org-1")
