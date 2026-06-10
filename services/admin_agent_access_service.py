from __future__ import annotations

"""
AO67H — Admin/Founder Agent Access Service

Purpose:
- Separate public visibility from founder/admin inspection.
- Public/AMCHAM users always resolve to Orkio.
- Founder/admin operators may directly inspect Orkio, Chris, Orion and sub-agents.
- No LLM call, no DB write, no network call and no deploy action.

Contract:
- Public surface: Orkio only.
- Admin surface: direct agent/sub-agent inspection allowed for authorized operators.
- Self-evolution write/deploy remains controlled by Daniel/founder authorization.
"""

import os
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set


PUBLIC_SPEAKER = "Orkio"
DEFAULT_ADMIN_COUNCIL = ("orkio", "chris", "orion")

RESERVED_INTERNAL_AGENT_SLUGS: Set[str] = {
    "chris",
    "orion",
    "cfo",
    "cto",
    "planner",
    "auditor",
    "architect",
    "devops",
    "sre",
    "security",
    "stage_manager",
    "memory_ops",
    "founder",
    "subagent",
    "sub_agent",
    "internal",
}

SENSITIVE_MODES: Set[str] = {
    "write",
    "deploy",
    "merge",
    "create_pr",
    "execute_patch",
    "self_evolution_write",
}

READONLY_MODES: Set[str] = {
    "readonly",
    "direct",
    "room",
    "meeting",
    "audit",
    "realtime",
    "diagnostic",
}

ADMIN_SURFACE_ALIASES: Set[str] = {
    "admin",
    "founder",
    "founder_admin",
    "founder-admin",
    "internal",
    "operator",
    "admin_room",
    "admin-agent-room",
    "admin_agent_room",
    "founder_room",
    "founder-agent-room",
    "founder_agent_room",
}


def is_admin_surface(surface: Any) -> bool:
    normalized = _clean(surface).lower() or "public"
    return normalized in ADMIN_SURFACE_ALIASES



def _clean(value: Any) -> str:
    raw = str(value or "").strip()
    if len(raw) >= 2 and ((raw[0] == raw[-1] == '"') or (raw[0] == raw[-1] == "'")):
        raw = raw[1:-1].strip()
    return raw.strip()


def normalize_agent_slug(value: Any) -> str:
    raw = _clean(value).lower()
    raw = raw.replace("@", "")
    raw = raw.replace(" ", "_")
    raw = re.sub(r"[^a-z0-9_\-\.]+", "", raw)
    aliases = {
        "orkio": "orkio",
        "órkio": "orkio",
        "orquio": "orkio",
        "chris": "chris",
        "cris": "chris",
        "orion": "orion",
        "órion": "orion",
    }
    return aliases.get(raw, raw)


def normalize_agent_list(values: Any) -> List[str]:
    if values is None:
        return []
    if isinstance(values, str):
        raw_items = re.split(r"[,;\n]+", values)
    elif isinstance(values, Iterable):
        raw_items = list(values)
    else:
        raw_items = [values]
    out: List[str] = []
    for item in raw_items:
        slug = normalize_agent_slug(item)
        if slug and slug not in out:
            out.append(slug)
    return out


def _payload_get(payload: Any, key: str, default: Any = None) -> Any:
    if payload is None:
        return default
    if isinstance(payload, dict):
        return payload.get(key, default)
    return getattr(payload, key, default)


def _csv_env(*keys: str) -> Set[str]:
    out: Set[str] = set()
    for key in keys:
        raw = _clean(os.getenv(key, ""))
        if not raw:
            continue
        for item in raw.split(","):
            norm = _clean(item).lower()
            if norm:
                out.add(norm)
    return out


def founder_admin_emails() -> Set[str]:
    return _csv_env(
        "ADMIN_MASTER_EMAILS",
        "MASTER_ADMIN_EMAILS",
        "ORKIO_ADMIN_MASTER_EMAILS",
        "SUPER_ADMIN_EMAILS",
        "ORKIO_FOUNDER_EMAILS",
        "FOUNDER_EMAILS",
    )


def extract_email(payload: Any) -> str:
    return _clean(
        _payload_get(payload, "email")
        or _payload_get(payload, "user_email")
        or _payload_get(payload, "preferred_username")
        or ""
    ).lower()


def extract_role(payload: Any) -> str:
    role = _clean(_payload_get(payload, "role") or "").lower()
    if role:
        return role
    if bool(_payload_get(payload, "is_admin")) or bool(_payload_get(payload, "admin")):
        return "admin"
    return "user"


def is_founder_or_admin(payload: Any) -> bool:
    role = extract_role(payload)
    email = extract_email(payload)
    allowed_roles = {
        "admin",
        "owner",
        "superadmin",
        "super_admin",
        "admin_master",
        "master_admin",
        "founder",
        "creator",
        "developer",
        "dev",
    }
    if role in allowed_roles:
        return True
    if email and email in founder_admin_emails():
        return True
    if bool(_payload_get(payload, "admin_console_access")):
        return True
    return False


def is_founder_master(payload: Any) -> bool:
    role = extract_role(payload)
    email = extract_email(payload)
    if role in {"admin_master", "master_admin", "founder", "creator", "owner"}:
        return True
    if email and email in founder_admin_emails():
        return True
    return False


@dataclass(frozen=True)
class AgentAccessDecision:
    ok: bool
    public_surface: bool
    admin_surface: bool
    requested_agent: str
    resolved_internal_agent: str
    public_speaker: str = PUBLIC_SPEAKER
    can_direct: bool = False
    can_room: bool = False
    can_realtime: bool = False
    can_see_internal_name: bool = False
    can_self_evolve_write: bool = False
    reason: str = ""
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def decide_agent_access(
    payload: Any,
    requested_agent: Any = "orkio",
    *,
    mode: str = "direct",
    surface: str = "public",
    allow_subagents: bool = True,
    founder_authorized: bool = False,
    **_: Any,
) -> AgentAccessDecision:
    """
    Resolve whether an operator may inspect or speak with an internal agent.

    Important:
    - Public users never receive internal agent identity.
    - Admin/founder users may inspect internal agents in admin surfaces.
    - Write/deploy/self-evolution write remains blocked unless founder_authorized=True
      and the operator is a founder/master admin.
    """
    agent = normalize_agent_slug(requested_agent) or "orkio"
    norm_mode = _clean(mode).lower() or "direct"
    norm_surface = _clean(surface).lower() or "public"

    admin = is_founder_or_admin(payload)
    founder = is_founder_master(payload)
    public_surface = not is_admin_surface(norm_surface)
    sensitive = norm_mode in SENSITIVE_MODES
    warnings: List[str] = []

    if public_surface:
        if agent != "orkio":
            warnings.append("internal_agent_resolved_to_orkio_for_public_surface")
        return AgentAccessDecision(
            ok=True,
            public_surface=True,
            admin_surface=False,
            requested_agent=agent,
            resolved_internal_agent="orkio",
            public_speaker=PUBLIC_SPEAKER,
            can_direct=False,
            can_room=False,
            can_realtime=True,
            can_see_internal_name=False,
            can_self_evolve_write=False,
            reason="public_surface_orkio_only",
            warnings=warnings,
        )

    if not admin:
        return AgentAccessDecision(
            ok=False,
            public_surface=False,
            admin_surface=False,
            requested_agent=agent,
            resolved_internal_agent="orkio",
            public_speaker=PUBLIC_SPEAKER,
            can_direct=False,
            can_room=False,
            can_realtime=False,
            can_see_internal_name=False,
            can_self_evolve_write=False,
            reason="admin_surface_requires_admin",
            warnings=["unauthorized_admin_agent_access"],
        )

    if not allow_subagents and agent not in {"orkio", "chris", "orion"}:
        return AgentAccessDecision(
            ok=False,
            public_surface=False,
            admin_surface=True,
            requested_agent=agent,
            resolved_internal_agent="orkio",
            public_speaker=PUBLIC_SPEAKER,
            can_direct=False,
            can_room=True,
            can_realtime=False,
            can_see_internal_name=True,
            can_self_evolve_write=False,
            reason="subagent_access_disabled",
            warnings=["subagent_requested_but_disabled"],
        )

    can_write = bool(founder and founder_authorized and sensitive)

    if sensitive and not can_write:
        warnings.append("sensitive_mode_requires_explicit_founder_authorization")

    return AgentAccessDecision(
        ok=True,
        public_surface=False,
        admin_surface=True,
        requested_agent=agent,
        resolved_internal_agent=agent,
        public_speaker=PUBLIC_SPEAKER,
        can_direct=True,
        can_room=True,
        can_realtime=True,
        can_see_internal_name=True,
        can_self_evolve_write=can_write,
        reason="admin_agent_access_granted_readonly" if not can_write else "founder_sensitive_access_granted",
        warnings=warnings,
    )


def public_agent_payload(agent_name: Any = "Orkio", **extra: Any) -> Dict[str, Any]:
    """
    Public-safe payload. Always masks internal names.
    """
    out = dict(extra or {})
    out.update(
        {
            "agent_name": PUBLIC_SPEAKER,
            "public_speaker": PUBLIC_SPEAKER,
            "resolve_to_public_speaker": PUBLIC_SPEAKER,
            "public_visible": True,
        }
    )
    return out


def admin_agent_payload(agent_slug: Any, *, payload: Any = None, **extra: Any) -> Dict[str, Any]:
    """
    Admin-safe payload. Shows internal name only to admin/founder operator.
    """
    agent = normalize_agent_slug(agent_slug) or "orkio"
    decision = decide_agent_access(payload, agent, surface="admin")
    out = dict(extra or {})
    out.update(
        {
            "agent_name": agent if decision.can_see_internal_name else PUBLIC_SPEAKER,
            "public_speaker": PUBLIC_SPEAKER,
            "resolve_to_public_speaker": PUBLIC_SPEAKER,
            "public_visible": False,
            "admin_visible": bool(decision.can_see_internal_name),
            "access": decision.to_dict(),
        }
    )
    return out
