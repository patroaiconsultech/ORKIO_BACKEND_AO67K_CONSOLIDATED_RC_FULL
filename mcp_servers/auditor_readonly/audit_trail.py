"""Append-only sanitized audit trail for MCP Auditor tool calls."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .auth import AuditorPrincipal
from .config import get_config
from .sanitizers import hash_identifier, sanitize_mapping, sanitize_text


def new_correlation_id() -> str:
    return str(uuid.uuid4())


def _safe_resource_refs(resource_refs: dict[str, Any] | None) -> dict[str, Any]:
    if not resource_refs:
        return {}
    safe: dict[str, Any] = {}
    for key, value in resource_refs.items():
        if value is None:
            safe[str(key)] = None
        elif str(key).endswith("_id") or str(key) in {"thread", "org", "user", "file"}:
            safe[str(key)] = hash_identifier(value)
        else:
            safe[str(key)] = sanitize_text(value, max_chars=160)
    return safe


def append_audit_event(
    *,
    correlation_id: str,
    principal: AuditorPrincipal | None,
    tool_name: str,
    outcome: str,
    resource_refs: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    cfg = get_config()
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
        "principal_ref": hash_identifier(principal.principal_id) if principal else None,
        "role": principal.role if principal else None,
        "tool": sanitize_text(tool_name, max_chars=120),
        "outcome": sanitize_text(outcome, max_chars=80),
        "resource_refs": _safe_resource_refs(resource_refs),
    }
    if error:
        event["error"] = sanitize_text(error, max_chars=300)

    path = Path(cfg.audit_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(sanitize_mapping(event), ensure_ascii=True, sort_keys=True) + "\n")
