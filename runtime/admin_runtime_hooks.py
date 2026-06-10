"""
AO68L — Admin Runtime Hooks for Orkio/PatroAI

Purpose:
- Keep public/beta users Orkio-only.
- Allow Daniel/admin/founder to access internal agents and realtime policy.
- Centralize admin-agent/realtime rules in one file.
- Avoid spreading admin exceptions across many routes.

Install with one small wiring point, preferably in main.py after app = FastAPI(...):

    try:
        from app.runtime.admin_runtime_hooks import install_admin_runtime_hooks
    except Exception:
        from runtime.admin_runtime_hooks import install_admin_runtime_hooks
    install_admin_runtime_hooks(app)

Existing routes can also import:
    get_admin_runtime_context(request)
    resolve_agent_slug(request, requested_agent)
    can_use_admin_realtime(request)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional

try:
    from fastapi import APIRouter, Request
except Exception:  # pragma: no cover - keeps module import-safe in tooling
    APIRouter = None  # type: ignore
    Request = Any  # type: ignore


_PUBLIC_AGENT = "orkio"
_DEFAULT_ADMIN_AGENTS = "orkio,chris,orion,auditor,planner,cfo,cto,subagent"
_DEFAULT_ADMIN_ROOM = "orkio,chris,orion"


def _csv(value: Optional[str], default: str = "") -> List[str]:
    raw = value if value is not None else default
    return [x.strip().lower() for x in raw.split(",") if x and x.strip()]


def _truthy(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on", "enabled"}


def _normalize_agent(agent: Optional[str]) -> str:
    slug = (agent or _PUBLIC_AGENT).strip().lower()
    aliases = {
        "orkio-ceo": "orkio",
        "orkio_ai": "orkio",
        "orion-tech": "orion",
        "chris-strategy": "chris",
    }
    return aliases.get(slug, slug or _PUBLIC_AGENT)


def _admin_emails() -> List[str]:
    emails = []
    for key in (
        "FOUNDER_ADMIN_EMAILS",
        "ORKIO_FOUNDER_EMAILS",
        "ORKIO_ADMIN_EMAILS",
        "ADMIN_EMAILS",
        "MASTER_ADMIN_EMAILS",
    ):
        emails.extend(_csv(os.getenv(key, "")))
    # Keep Daniel's canonical admin email as safe default for staging.
    if not emails:
        emails = ["daniel@patroai.com"]
    return sorted(set(emails))


def _roles_from_claims(claims: Dict[str, Any]) -> List[str]:
    roles: List[str] = []
    for key in ("role", "roles", "scope", "scopes", "permissions"):
        val = claims.get(key)
        if isinstance(val, str):
            roles.extend(_csv(val.replace(" ", ",")))
        elif isinstance(val, Iterable):
            roles.extend(str(x).strip().lower() for x in val if str(x).strip())
    return sorted(set(roles))


def _email_from_claims(claims: Dict[str, Any]) -> str:
    for key in ("email", "user_email", "sub_email", "preferred_username"):
        val = claims.get(key)
        if val:
            return str(val).strip().lower()
    return ""


def _decode_bearer_token(token: str) -> Dict[str, Any]:
    """
    Best-effort decode using project security module.
    Returns {} if token is absent/invalid or the decoder is unavailable.
    """
    if not token:
        return {}
    candidates = (
        "app.security",
        "security",
    )
    for module_name in candidates:
        try:
            import importlib

            mod = importlib.import_module(module_name)
            decoder = getattr(mod, "decode_token", None)
            if callable(decoder):
                decoded = decoder(token)
                return decoded if isinstance(decoded, dict) else {}
        except Exception:
            continue
    return {}


def _claims_from_request(request: Request) -> Dict[str, Any]:
    try:
        auth = request.headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            return _decode_bearer_token(auth.split(" ", 1)[1].strip())
    except Exception:
        return {}
    return {}


@dataclass(frozen=True)
class AdminRuntimeContext:
    is_admin: bool
    email: str
    roles: List[str]
    public_agent: str
    allowed_agent_slugs: List[str]
    room_principal_agents: List[str]
    public_realtime_orkio_only: bool
    admin_realtime_enabled: bool
    admin_agent_room_enabled: bool
    admin_direct_agent_enabled: bool
    admin_visible_internal_agents: bool
    public_visible_internal_agents: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_admin_runtime_context(claims: Optional[Dict[str, Any]] = None) -> AdminRuntimeContext:
    claims = claims or {}
    email = _email_from_claims(claims)
    roles = _roles_from_claims(claims)
    admin_role_names = {"admin", "founder", "owner", "superadmin", "master_admin", "daniel"}
    is_admin = bool(
        email in _admin_emails()
        or any(role in admin_role_names for role in roles)
        or str(claims.get("is_admin", "")).lower() == "true"
        or str(claims.get("founder", "")).lower() == "true"
    )

    return AdminRuntimeContext(
        is_admin=is_admin,
        email=email,
        roles=roles,
        public_agent=_PUBLIC_AGENT,
        allowed_agent_slugs=_csv(os.getenv("ORKIO_ADMIN_ALLOWED_AGENT_SLUGS"), _DEFAULT_ADMIN_AGENTS),
        room_principal_agents=_csv(os.getenv("ORKIO_ADMIN_ROOM_PRINCIPAL_AGENTS"), _DEFAULT_ADMIN_ROOM),
        public_realtime_orkio_only=_truthy(os.getenv("ORKIO_PUBLIC_REALTIME_ORKIO_ONLY"), True),
        admin_realtime_enabled=_truthy(os.getenv("ORKIO_ADMIN_REALTIME_ENABLED"), True),
        admin_agent_room_enabled=_truthy(os.getenv("ORKIO_ADMIN_AGENT_ROOM_ENABLED"), True),
        admin_direct_agent_enabled=_truthy(os.getenv("ORKIO_ADMIN_DIRECT_AGENT_ENABLED"), True),
        admin_visible_internal_agents=_truthy(os.getenv("ORKIO_ADMIN_VISIBLE_INTERNAL_AGENTS"), True),
        public_visible_internal_agents=_truthy(os.getenv("ORKIO_PUBLIC_VISIBLE_INTERNAL_AGENTS"), False),
    )


def get_admin_runtime_context(request: Request) -> AdminRuntimeContext:
    existing = getattr(getattr(request, "state", None), "orkio_admin_runtime", None)
    if isinstance(existing, AdminRuntimeContext):
        return existing
    ctx = build_admin_runtime_context(_claims_from_request(request))
    try:
        request.state.orkio_admin_runtime = ctx
    except Exception:
        pass
    return ctx


def resolve_agent_slug(request: Request, requested_agent: Optional[str]) -> str:
    """
    Public users always resolve to Orkio.
    Admin users can resolve to configured internal agents.
    """
    ctx = get_admin_runtime_context(request)
    slug = _normalize_agent(requested_agent)
    if not ctx.is_admin:
        return ctx.public_agent
    if slug in ctx.allowed_agent_slugs:
        return slug
    return ctx.public_agent


def can_use_admin_realtime(request: Request) -> bool:
    ctx = get_admin_runtime_context(request)
    return bool(ctx.is_admin and ctx.admin_realtime_enabled)


def can_use_admin_agent_room(request: Request) -> bool:
    ctx = get_admin_runtime_context(request)
    return bool(ctx.is_admin and ctx.admin_agent_room_enabled)


def build_room_agents(request: Request, requested_agents: Optional[List[str]] = None) -> List[str]:
    ctx = get_admin_runtime_context(request)
    if not ctx.is_admin:
        return [ctx.public_agent]
    wanted = requested_agents or ctx.room_principal_agents
    safe: List[str] = []
    for agent in wanted:
        slug = _normalize_agent(agent)
        if slug in ctx.allowed_agent_slugs and slug not in safe:
            safe.append(slug)
    return safe or [ctx.public_agent]


def _router():
    if APIRouter is None:
        return None
    router = APIRouter(tags=["admin-runtime-hooks"])

    @router.get("/api/admin/runtime/capabilities")
    async def admin_runtime_capabilities(request: Request):
        ctx = get_admin_runtime_context(request)
        if not ctx.is_admin:
            return {
                "ok": True,
                "is_admin": False,
                "public_agent": ctx.public_agent,
                "allowed_agent_slugs": [ctx.public_agent],
                "admin_realtime_enabled": False,
                "admin_agent_room_enabled": False,
                "visible_internal_agents": False,
            }
        return {
            "ok": True,
            **ctx.to_dict(),
            "visible_internal_agents": ctx.admin_visible_internal_agents,
        }

    @router.post("/api/admin/runtime/resolve-agent")
    async def admin_runtime_resolve_agent(request: Request):
        try:
            body = await request.json()
        except Exception:
            body = {}
        requested_agent = body.get("agent") or body.get("agent_id") or body.get("slug")
        resolved = resolve_agent_slug(request, requested_agent)
        ctx = get_admin_runtime_context(request)
        return {
            "ok": True,
            "is_admin": ctx.is_admin,
            "requested_agent": requested_agent,
            "resolved_agent": resolved,
            "public_fallback": not ctx.is_admin,
        }

    @router.post("/api/admin/runtime/room-plan")
    async def admin_runtime_room_plan(request: Request):
        try:
            body = await request.json()
        except Exception:
            body = {}
        requested = body.get("agents")
        if not isinstance(requested, list):
            requested = None
        ctx = get_admin_runtime_context(request)
        agents = build_room_agents(request, requested)
        return {
            "ok": True,
            "is_admin": ctx.is_admin,
            "room_enabled": bool(ctx.is_admin and ctx.admin_agent_room_enabled),
            "agents": agents,
            "public_fallback": not ctx.is_admin,
        }

    @router.get("/api/admin/realtime/policy")
    async def admin_realtime_policy(request: Request):
        ctx = get_admin_runtime_context(request)
        return {
            "ok": True,
            "is_admin": ctx.is_admin,
            "public_realtime_orkio_only": ctx.public_realtime_orkio_only,
            "admin_realtime_enabled": bool(ctx.is_admin and ctx.admin_realtime_enabled),
            "allowed_agent_slugs": ctx.allowed_agent_slugs if ctx.is_admin else [ctx.public_agent],
        }

    return router


def install_admin_runtime_hooks(app: Any) -> None:
    """
    Idempotent FastAPI installer.
    Adds a lightweight middleware and admin-runtime routes.
    """
    if getattr(app.state, "ao68l_admin_runtime_hooks_installed", False):
        return

    @app.middleware("http")
    async def ao68l_admin_runtime_context_middleware(request: Request, call_next):
        try:
            request.state.orkio_admin_runtime = build_admin_runtime_context(_claims_from_request(request))
        except Exception:
            pass
        return await call_next(request)

    router = _router()
    if router is not None:
        app.include_router(router)

    app.state.ao68l_admin_runtime_hooks_installed = True
