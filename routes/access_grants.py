from __future__ import annotations

import hashlib
import hmac
import ipaddress
import json
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models import AuditLog
from app.schemas.access_grants import (
    AccessGrantOut,
    AccessGrantStatusOut,
    AccessGrantValidateIn,
)
from app.services.access_grant_service import (
    AccessGrantConfigurationError,
    AccessGrantInvalidError,
    clear_access_grant_cookie,
    decode_access_grant,
    find_signup_code,
    find_signup_code_by_id,
    issue_access_grant,
    load_access_grant_config,
    access_gate_header_transport_enabled,
    set_access_grant_cookie,
)


@dataclass(frozen=True)
class AccessGrantRouterDeps:
    get_db: Callable[..., Any]
    get_org: Callable[[Optional[str]], str]
    new_id: Callable[[], str]
    now_ts: Callable[[], int]
    logger: Any


def _validated_ip(value: str) -> Optional[str]:
    candidate = str(value or "").strip()
    if not candidate:
        return None
    try:
        return str(ipaddress.ip_address(candidate))
    except ValueError:
        return None


def _client_ip(request: Request, *, trust_proxy_headers: bool) -> str:
    if trust_proxy_headers:
        candidates = [
            request.headers.get("railway-client-ip", ""),
            request.headers.get("cf-connecting-ip", ""),
            request.headers.get("x-real-ip", ""),
        ]
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            candidates.extend(part.strip() for part in forwarded.split(","))
        for candidate in candidates:
            validated = _validated_ip(candidate)
            if validated:
                return validated

    if request.client and request.client.host:
        return str(request.client.host)
    return "unknown"


def _ip_ref(request: Request, *, signing_key: str, trust_proxy_headers: bool) -> str:
    client_ip = _client_ip(request, trust_proxy_headers=trust_proxy_headers)
    return hmac.new(
        signing_key.encode("utf-8"),
        client_ip.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:24]


def _advisory_lock_key(value: str) -> int:
    raw = hashlib.sha256(value.encode("utf-8")).digest()[:8]
    return int.from_bytes(raw, byteorder="big", signed=True)


def _lock_rate_bucket(db: Session, bucket: str) -> None:
    """Serialize attempts across replicas when PostgreSQL is authoritative.

    SQLite and other local test dialects do not expose PostgreSQL advisory locks.
    In production PostgreSQL, a lock failure is fail-closed because continuing
    would make the attempt counter race-prone across replicas.
    """
    bind = db.get_bind()
    if bind is None or bind.dialect.name != "postgresql":
        return
    try:
        db.execute(
            text("SELECT pg_advisory_xact_lock(:key)"),
            {"key": _advisory_lock_key(bucket)},
        )
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="ACCESS_GATE_RATE_LIMIT_UNAVAILABLE",
        ) from exc


def _write_audit(
    *,
    db: Session,
    deps: AccessGrantRouterDeps,
    request: Request,
    org_slug: str,
    action: str,
    status_code: int,
    ip_ref: str,
    purpose: str,
    code_id: Optional[str] = None,
) -> None:
    cfg = load_access_grant_config()
    if not cfg.audit_enabled:
        return
    db.add(
        AuditLog(
            id=deps.new_id(),
            org_slug=org_slug,
            user_id=f"access_gate:{ip_ref}",
            action=action,
            meta=json.dumps(
                {
                    "purpose": purpose,
                    "code_id": code_id,
                    "ip_ref": ip_ref,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            request_id=(
                request.headers.get("x-request-id")
                or request.headers.get("x-railway-request-id")
                or deps.new_id()
            ),
            path="/api/access-grants/validate",
            status_code=status_code,
            latency_ms=0,
            created_at=deps.now_ts(),
        )
    )


def build_access_grants_router(deps: AccessGrantRouterDeps) -> APIRouter:
    router = APIRouter(prefix="/api/access-grants", tags=["access-grants"])

    @router.post("/validate", response_model=AccessGrantOut)
    def validate_access_grant(
        payload: AccessGrantValidateIn,
        response: Response,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        db: Session = Depends(deps.get_db),
    ):
        try:
            cfg = load_access_grant_config(require_signing_key=True)
        except AccessGrantConfigurationError as exc:
            deps.logger.error("ACCESS_GATE_CONFIG_INVALID reason=%s", exc)
            raise HTTPException(status_code=503, detail="ACCESS_GATE_NOT_CONFIGURED")

        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        org = deps.get_org(x_org_slug)
        ip_ref = _ip_ref(
            request,
            signing_key=cfg.signing_key,
            trust_proxy_headers=cfg.trust_proxy_headers,
        )
        bucket = f"{org}:{ip_ref}"
        _lock_rate_bucket(db, bucket)

        cutoff = deps.now_ts() - cfg.rate_window_seconds
        denied_actions = (
            "access_gate.validate.denied",
            "access_gate.validate.rate_limited",
        )
        recent_denied = db.execute(
            select(func.count(AuditLog.id)).where(
                AuditLog.org_slug == org,
                AuditLog.user_id == f"access_gate:{ip_ref}",
                AuditLog.action.in_(denied_actions),
                AuditLog.created_at >= cutoff,
            )
        ).scalar_one()

        if int(recent_denied or 0) >= cfg.max_attempts:
            _write_audit(
                db=db,
                deps=deps,
                request=request,
                org_slug=org,
                action="access_gate.validate.rate_limited",
                status_code=429,
                ip_ref=ip_ref,
                purpose=payload.purpose,
            )
            db.commit()
            raise HTTPException(status_code=429, detail="ACCESS_GATE_RATE_LIMITED")

        code = find_signup_code(
            db,
            org_slug=org,
            plain_code=payload.code,
            consume=False,
            now=deps.now_ts(),
        )
        if code is None:
            _write_audit(
                db=db,
                deps=deps,
                request=request,
                org_slug=org,
                action="access_gate.validate.denied",
                status_code=401,
                ip_ref=ip_ref,
                purpose=payload.purpose,
            )
            db.commit()
            raise HTTPException(status_code=401, detail="INVALID_ACCESS_CODE")

        token, claims = issue_access_grant(
            code=code,
            org_slug=org,
            purpose=payload.purpose,
            user_agent=request.headers.get("user-agent", ""),
            now=deps.now_ts(),
            config=cfg,
        )
        _write_audit(
            db=db,
            deps=deps,
            request=request,
            org_slug=org,
            action="access_gate.validate.granted",
            status_code=200,
            ip_ref=ip_ref,
            purpose=payload.purpose,
            code_id=str(code.id),
        )
        db.commit()
        set_access_grant_cookie(response, token, cfg)

        return AccessGrantOut(
            granted=True,
            purpose=payload.purpose,
            expires_at=int(claims["exp"]),
            scope=list(claims.get("scope") or []),
            grant_token=(
                token if access_gate_header_transport_enabled() else None
            ),
        )

    @router.get("/status", response_model=AccessGrantStatusOut)
    def access_grant_status(
        request: Request,
        response: Response,
        x_org_slug: Optional[str] = Header(default=None),
        db: Session = Depends(deps.get_db),
    ):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        try:
            cfg = load_access_grant_config(require_signing_key=True)
        except AccessGrantConfigurationError:
            return AccessGrantStatusOut(granted=False)

        token = request.cookies.get(cfg.cookie_name)
        if not token:
            return AccessGrantStatusOut(granted=False)

        org = deps.get_org(x_org_slug)
        try:
            claims = decode_access_grant(
                token,
                expected_org=org,
                user_agent=request.headers.get("user-agent", ""),
                now=deps.now_ts(),
                config=cfg,
            )
        except AccessGrantInvalidError:
            return AccessGrantStatusOut(granted=False)

        code = find_signup_code_by_id(
            db,
            org_slug=org,
            code_id=str(claims.get("code_id") or ""),
            consume=False,
            now=deps.now_ts(),
        )
        if code is None:
            return AccessGrantStatusOut(granted=False)

        return AccessGrantStatusOut(
            granted=True,
            purpose=str(claims.get("purpose") or ""),
            expires_at=int(claims.get("exp") or 0),
            scope=list(claims.get("scope") or []),
        )

    @router.post("/revoke", response_model=AccessGrantStatusOut)
    def revoke_access_grant(response: Response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        cfg = load_access_grant_config()
        clear_access_grant_cookie(response, cfg)
        return AccessGrantStatusOut(granted=False)

    return router
