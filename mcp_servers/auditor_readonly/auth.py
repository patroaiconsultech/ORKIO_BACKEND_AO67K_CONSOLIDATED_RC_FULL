"""Operational authentication identity for the readonly MCP Auditor.

The MCP process must be placed behind external authentication. This module
creates the internal principal used for RBAC decisions and audit trail events.
It does not expose secrets and does not authenticate end users.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import AuditorConfig, get_config


class AuditorAuthError(PermissionError):
    """Raised when the readonly MCP auditor is not allowed to serve a request."""


@dataclass(frozen=True)
class AuditorPrincipal:
    principal_id: str
    role: str
    allowed_tools: tuple[str, ...]
    allowed_org_ids: tuple[str, ...]

    @property
    def is_readonly_auditor(self) -> bool:
        return self.role == "readonly_auditor"


def principal_from_config(config: AuditorConfig | None = None) -> AuditorPrincipal:
    cfg = config or get_config()
    if not cfg.enabled:
        raise AuditorAuthError("MCP auditor disabled")
    if cfg.role != "readonly_auditor":
        raise AuditorAuthError("invalid auditor role")
    if not cfg.allowed_tools:
        raise AuditorAuthError("no tools allowed")
    if not cfg.allowed_org_ids:
        raise AuditorAuthError("no organization scope configured")
    return AuditorPrincipal(
        principal_id=cfg.principal_id,
        role=cfg.role,
        allowed_tools=cfg.allowed_tools,
        allowed_org_ids=cfg.allowed_org_ids,
    )
