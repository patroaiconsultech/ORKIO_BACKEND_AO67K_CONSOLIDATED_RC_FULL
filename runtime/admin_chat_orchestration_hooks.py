"""AO68B-HF1_ADMIN_AUTH_PARITY — expanded admin detection for chat orchestration."""
"""
AO68M — Admin Chat Orchestration Hooks

Purpose:
- Keep public users protected by Orkio-only policy.
- Let Daniel/admin bypass the public internal-agent block inside /api/chat/stream.
- Avoid touching many route files.
- Provide a single importable helper for chat gateway/admin orchestration decisions.

This module does not write to GitHub, deploy, DB, or external services.
It only decides whether the public decision-mesh fastpath should be bypassed
so the normal chat/realtime/orchestration path can continue for an admin.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, Iterable, List, Optional


PUBLIC_AGENT = "orkio"
DEFAULT_INTERNAL_AGENTS = "chris,orion,auditor,planner,cfo,cto,subagent"


def _truthy(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    raw = str(value).strip().lower()
    if raw in {"1", "true", "yes", "y", "on", "enabled", "enable"}:
        return True
    if raw in {"0", "false", "no", "n", "off", "disabled", "disable"}:
        return False
    return default


def _csv(value: Optional[str], default: str = "") -> List[str]:
    raw = value if value is not None else default
    return [x.strip().lower() for x in str(raw).split(",") if x and x.strip()]


def _normalize_agent(agent: Any) -> str:
    slug = str(agent or "").strip().lower()
    aliases = {
        "@orkio": "orkio",
        "orkio-ceo": "orkio",
        "orkio_ai": "orkio",
        "@orion": "orion",
        "orion-tech": "orion",
        "orion_tech": "orion",
        "@chris": "chris",
        "chris-strategy": "chris",
        "chris_strategy": "chris",
        "@auditor": "auditor",
        "@planner": "planner",
        "@cfo": "cfo",
        "@cto": "cto",
    }
    return aliases.get(slug, slug or PUBLIC_AGENT)


def _get_value(obj: Any, *keys: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        for key in keys:
            if key in obj and obj.get(key) not in (None, ""):
                return obj.get(key)
        return None
    for key in keys:
        val = getattr(obj, key, None)
        if val not in (None, ""):
            return val
    return None


def _roles_from_user(user: Any) -> List[str]:
    roles: List[str] = []
    raw = _get_value(user, "role", "roles", "scope", "scopes", "permissions")
    if isinstance(raw, str):
        roles.extend(_csv(raw.replace(" ", ",")))
    elif isinstance(raw, Iterable):
        roles.extend(str(x).strip().lower() for x in raw if str(x).strip())
    return sorted(set(roles))


def _email_from_user(user: Any) -> str:
    val = _get_value(user, "email", "user_email", "sub_email", "preferred_username")
    return str(val or "").strip().lower()


def _admin_emails() -> List[str]:
    emails: List[str] = []
    for key in (
        "FOUNDER_ADMIN_EMAILS",
        "ORKIO_FOUNDER_EMAILS",
        "ORKIO_SUPER_ADMIN_EMAILS",
        "ORKIO_ADMIN_EMAILS",
        "SUPER_ADMIN_EMAILS",
        "ADMIN_EMAILS",
        "MASTER_ADMIN_EMAILS",
    ):
        emails.extend(_csv(os.getenv(key, "")))
    if not emails:
        emails = ["daniel@patroai.com"]
    return sorted(set(emails))


def is_admin_user(user: Any = None, *, org_slug: Optional[str] = None, route_plan: Optional[Dict[str, Any]] = None) -> bool:
    """Conservative admin check.

    It should be true only for authenticated founder/admin context. Public users remain Orkio-only.
    """
    roles = _roles_from_user(user)
    email = _email_from_user(user)
    admin_roles = {"admin", "founder", "owner", "superadmin", "master_admin", "daniel"}

    if email and email in _admin_emails():
        return True
    if any(role in admin_roles for role in roles):
        return True
    if _truthy(_get_value(
        user,
        "is_admin",
        "admin",
        "admin_console_access",
        "is_admin_master",
        "super_admin",
        "is_super_admin",
        "founder",
        "is_founder",
        "write_approval_authority",
    ), False):
        return True

    # Optional trusted backend route-plan signal. Use only if backend built it,
    # not as a public frontend security control.
    try:
        admin_runtime = dict((route_plan or {}).get("admin_runtime") or {})
        if admin_runtime.get("is_admin") is True and _truthy(os.getenv("ORKIO_TRUST_BACKEND_ADMIN_ROUTE_PLAN"), False):
            return True
    except Exception:
        pass

    return False


def _extract_message_text(message: Any) -> str:
    if message is None:
        return ""
    if isinstance(message, str):
        return message
    if isinstance(message, dict):
        for key in ("content", "text", "message", "prompt", "user_message", "input", "body"):
            val = message.get(key)
            if val:
                return str(val)
    for key in ("content", "text", "message", "prompt", "user_message", "input", "body"):
        val = getattr(message, key, None)
        if val:
            return str(val)
    return str(message or "")


def requested_agent_from_chat(
    *,
    message: Any,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
    dest_mode: Any = None,
    route_plan: Optional[Dict[str, Any]] = None,
) -> str:
    candidates: List[Any] = [
        target_agent_slug,
        visible_agent,
        dest_mode,
    ]

    rp = route_plan or {}
    for key in ("target_agent_slug", "agent_id", "agent", "visible_agent", "requested_agent", "selected_agent"):
        candidates.append(rp.get(key))

    text = _extract_message_text(message).lower()

    # Explicit mentions.
    mention_patterns = {
        "orion": r"(^|\s)@?orion\b",
        "chris": r"(^|\s)@?chris\b",
        "auditor": r"(^|\s)@?auditor\b",
        "planner": r"(^|\s)@?planner\b",
        "cfo": r"(^|\s)@?cfo\b",
        "cto": r"(^|\s)@?cto\b",
    }
    for agent, pattern in mention_patterns.items():
        if re.search(pattern, text):
            candidates.insert(0, agent)
            break

    for candidate in candidates:
        slug = _normalize_agent(candidate)
        if slug and slug != PUBLIC_AGENT:
            return slug

    return PUBLIC_AGENT


def allowed_admin_agents() -> List[str]:
    agents = _csv(os.getenv("ORKIO_ADMIN_ALLOWED_AGENT_SLUGS"), DEFAULT_INTERNAL_AGENTS)
    if PUBLIC_AGENT not in agents:
        agents.insert(0, PUBLIC_AGENT)
    return sorted(set(agents))


def build_admin_chat_gateway_override(
    *,
    message: Any,
    user: Any = None,
    org_slug: Optional[str] = None,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
    dest_mode: Any = None,
    route_plan: Optional[Dict[str, Any]] = None,
    thread_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Return a gateway decision only when admin should bypass public fastpath.

    handled=False is intentional: it prevents the public decision-mesh canned block
    from short-circuiting the stream, while letting the normal chat/realtime/
    orchestration route continue downstream.
    """
    if not _truthy(os.getenv("ORKIO_ADMIN_CHAT_GATEWAY_OVERRIDE_ENABLED"), True):
        return None

    requested_agent = requested_agent_from_chat(
        message=message,
        visible_agent=visible_agent,
        target_agent_slug=target_agent_slug,
        dest_mode=dest_mode,
        route_plan=route_plan,
    )

    if requested_agent == PUBLIC_AGENT:
        return None

    if requested_agent not in allowed_admin_agents():
        return None

    if not is_admin_user(user, org_slug=org_slug, route_plan=route_plan):
        return None

    return {
        "ok": True,
        "handled": False,
        "reason": "admin_internal_agent_bypass_public_gateway",
        "service": "admin_chat_orchestration_hooks",
        "version": "AO68M_ADMIN_CHAT_GATEWAY_ORCHESTRATION_BYPASS_V1",
        "admin_override": True,
        "admin_internal_agent_allowed": True,
        "agent_id": requested_agent,
        "agent_name": requested_agent.title(),
        "target_agent_slug": requested_agent,
        "final_speaker": requested_agent.title(),
        "visible_agent": requested_agent.title(),
        "thread_id": thread_id,
        "user_id": user_id,
        "public_speaker": "Orkio",
        "public_short_circuit_blocked": True,
        "runtime_hints": {
            "admin_chat_gateway_override": {
                "enabled": True,
                "reason": "admin_internal_agent_bypass_public_gateway",
                "requested_agent": requested_agent,
                "public_users_remain_orkio_only": True,
                "handled": False,
                "rule": "admin_bypasses_public_internal_agent_block_then_normal_orchestration_continues",
            }
        },
    }
