import json

from mcp_servers.auditor_readonly import tools
from mcp_servers.auditor_readonly.config import reload_config


def configure_tools(monkeypatch, tmp_path):
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ENABLED", "true")
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_EXTERNAL_AUTH_REQUIRED", "true")
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_PRINCIPAL_ID", "mcp_auditor_readonly")
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ROLE", "readonly_auditor")
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_ALLOWED_ORG_IDS", "org-1")
    monkeypatch.setenv(
        "ORKIO_MCP_AUDITOR_ALLOWED_TOOLS",
        "get_health,get_recent_logs_sanitized,get_thread_metadata,get_message_counts,get_file_refs,get_runtime_flags,get_audit_reports",
    )
    monkeypatch.setenv("ORKIO_MCP_AUDITOR_AUDIT_LOG_PATH", str(tmp_path / "audit.jsonl"))
    reload_config()


def test_get_health_returns_contract_and_writes_sanitized_audit(monkeypatch, tmp_path):
    configure_tools(monkeypatch, tmp_path)
    monkeypatch.setattr(
        tools,
        "get_health_snapshot",
        lambda: {
            "status": "ok",
            "database": {"configured": True, "connectivity": "ok"},
            "external_auth_required": True,
            "enabled": True,
            "readonly": True,
        },
    )

    result = tools.get_health()

    assert result["ok"] is True
    assert result["tool"] == "get_health"
    assert result["readonly"] is True
    audit_path = tmp_path / "audit.jsonl"
    assert audit_path.exists()
    events = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert events[0]["tool"] == "get_health"
    assert events[-1]["outcome"] == "ok"
    assert "mcp_auditor_readonly" not in audit_path.read_text(encoding="utf-8")


def test_get_thread_metadata_blocks_disallowed_org(monkeypatch, tmp_path):
    configure_tools(monkeypatch, tmp_path)

    result = tools.get_thread_metadata(thread_id="thread-1", org_id="org-2")

    assert result["ok"] is False
    assert result["tool"] == "get_thread_metadata"
    assert result["error"]["type"] in {"AuditorPermissionError", "PermissionError"}


def test_get_thread_metadata_returns_metadata_without_content(monkeypatch, tmp_path):
    configure_tools(monkeypatch, tmp_path)
    monkeypatch.setattr(
        tools,
        "fetch_thread_metadata",
        lambda thread_id, org_id=None: {
            "thread_ref": "sha256:thread",
            "organization_id": "sha256:org",
            "user_id": "sha256:user",
            "status": "active",
        },
    )

    result = tools.get_thread_metadata(thread_id="thread-1", org_id="org-1")

    assert result["ok"] is True
    assert result["thread"]["status"] == "active"
    assert "content" not in result["thread"]
    assert "messages" not in result["thread"]


def test_get_message_counts_returns_counts_only(monkeypatch, tmp_path):
    configure_tools(monkeypatch, tmp_path)
    monkeypatch.setattr(
        tools,
        "fetch_message_counts",
        lambda thread_id, org_id=None: {
            "thread_ref": "sha256:thread",
            "total": 3,
            "by_role": {"user": 1, "assistant": 2},
            "by_status": {"completed": 3},
            "latest_message_at": None,
        },
    )

    result = tools.get_message_counts(thread_id="thread-1", org_id="org-1")

    assert result["ok"] is True
    assert result["counts"]["total"] == 3
    assert "content" not in result["counts"]


def test_get_file_refs_returns_refs_only(monkeypatch, tmp_path):
    configure_tools(monkeypatch, tmp_path)
    monkeypatch.setattr(
        tools,
        "fetch_file_refs",
        lambda thread_id, org_id=None, limit=None: [
            {
                "file_ref": "sha256:file",
                "filename_ref": "sha256:filename",
                "extension": ".pdf",
                "status": "indexed",
            }
        ],
    )

    result = tools.get_file_refs(thread_id="thread-1", org_id="org-1")

    assert result["ok"] is True
    assert result["files"][0]["extension"] == ".pdf"
    assert "extracted_text" not in result["files"][0]
    assert "content" not in result["files"][0]
