from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from dataclasses import dataclass
from typing import Any, Mapping, Optional

from fastapi import HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SignupCode


ACCESS_GRANT_VERSION = "SEC001_ACCESS_GRANT_V1"
_ALLOWED_PURPOSES = {
    "platform_beta",
    "summit_general",
    "summit_investor",
    "partner",
}
_COOKIE_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")


class AccessGrantConfigurationError(RuntimeError):
    pass


class AccessGrantInvalidError(ValueError):
    pass


@dataclass(frozen=True)
class AccessGrantConfig:
    enabled: bool
    require_for_auth: bool
    signing_key: str
    cookie_name: str
    ttl_seconds: int
    cookie_secure: bool
    cookie_samesite: str
    bind_user_agent: bool
    trust_proxy_headers: bool
    max_attempts: int
    rate_window_seconds: int
    audit_enabled: bool


def _clean_env(value: Optional[str], default: str = "") -> str:
    text = str(value if value is not None else default).strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        text = text[1:-1].strip()
    return text


def _env_bool(name: str, default: bool) -> bool:
    raw = _clean_env(os.getenv(name), "true" if default else "false").lower()
    return raw in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(_clean_env(os.getenv(name), str(default)))
    except Exception:
        value = default
    return max(minimum, min(maximum, value))


def load_access_grant_config(*, require_signing_key: bool = False) -> AccessGrantConfig:
    enabled = _env_bool("ACCESS_GATE_SERVER_SIDE_ONLY", False)
    require_for_auth = _env_bool("ACCESS_GATE_REQUIRE_FOR_AUTH", enabled)
    signing_key = _clean_env(os.getenv("ACCESS_GATE_SIGNING_KEY"), "")
    cookie_name = _clean_env(os.getenv("ACCESS_GATE_COOKIE_NAME"), "orkio_access_grant")
    if not _COOKIE_NAME_RE.fullmatch(cookie_name):
        raise AccessGrantConfigurationError("invalid_access_gate_cookie_name")

    same_site = _clean_env(os.getenv("ACCESS_GATE_COOKIE_SAMESITE"), "lax").lower()
    if same_site not in {"lax", "strict", "none"}:
        raise AccessGrantConfigurationError("invalid_access_gate_cookie_samesite")

    cookie_secure = _env_bool(
        "ACCESS_GATE_COOKIE_SECURE",
        _clean_env(os.getenv("APP_ENV"), "production").lower() == "production",
    )
    if same_site == "none" and not cookie_secure:
        raise AccessGrantConfigurationError("samesite_none_requires_secure_cookie")

    config = AccessGrantConfig(
        enabled=enabled,
        require_for_auth=require_for_auth,
        signing_key=signing_key,
        cookie_name=cookie_name,
        ttl_seconds=_env_int("ACCESS_GRANT_TTL_SECONDS", 86400, 300, 604800),
        cookie_secure=cookie_secure,
        cookie_samesite=same_site,
        bind_user_agent=_env_bool("ACCESS_GATE_BIND_USER_AGENT", True),
        trust_proxy_headers=_env_bool("ACCESS_GATE_TRUST_PROXY_HEADERS", False),
        max_attempts=_env_int("ACCESS_CODE_MAX_ATTEMPTS", 5, 1, 100),
        rate_window_seconds=_env_int("ACCESS_CODE_RATE_WINDOW_SECONDS", 300, 30, 86400),
        audit_enabled=_env_bool("ACCESS_AUDIT_ENABLED", True),
    )

    if require_signing_key or enabled or require_for_auth:
        if len(signing_key.encode("utf-8")) < 32:
            raise AccessGrantConfigurationError(
                "ACCESS_GATE_SIGNING_KEY must contain at least 32 bytes"
            )
    return config


def access_gate_auth_required() -> bool:
    return load_access_grant_config().require_for_auth


def normalize_access_code(value: Optional[str]) -> str:
    return re.sub(r"\s+", "", str(value or "")).strip().upper()


def hash_access_code(value: Optional[str]) -> str:
    normalized = normalize_access_code(value)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def normalize_purpose(value: Optional[str]) -> str:
    purpose = str(value or "platform_beta").strip().lower()
    if purpose not in _ALLOWED_PURPOSES:
        raise AccessGrantInvalidError("unsupported_access_grant_purpose")
    return purpose


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(raw: str) -> bytes:
    padding = "=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode((raw + padding).encode("ascii"))


def _ua_hash(user_agent: str) -> str:
    return hashlib.sha256(str(user_agent or "").encode("utf-8")).hexdigest()[:32]


def _scope_for_code(code: SignupCode, purpose: str) -> list[str]:
    source = str(getattr(code, "source", "") or "").strip().lower()
    label = str(getattr(code, "label", "") or "").strip().lower()
    scopes = {"platform"}
    if purpose:
        scopes.add(purpose)
    if source == "investor" or "investor" in label:
        scopes.add("summit_investor")
    if source == "amcham_rs_partner" or "partner" in label:
        scopes.add("partner")
    if source == "summit_user" or "summit" in label:
        scopes.add("summit_general")
    return sorted(scopes)


def find_signup_code(
    db: Session,
    *,
    org_slug: str,
    plain_code: str,
    consume: bool = False,
    now: Optional[int] = None,
) -> Optional[SignupCode]:
    normalized = normalize_access_code(plain_code)
    if not normalized:
        return None

    query = select(SignupCode).where(
        SignupCode.org_slug == str(org_slug or "public").strip(),
        SignupCode.code_hash == hash_access_code(normalized),
        SignupCode.active.is_(True),
    )
    if consume:
        query = query.with_for_update()

    row = db.execute(query).scalar_one_or_none()
    if row is None:
        return None

    current = int(now or time.time())
    expires_at = int(getattr(row, "expires_at", 0) or 0)
    if expires_at and expires_at < current:
        return None

    used_count = int(getattr(row, "used_count", 0) or 0)
    max_uses = int(getattr(row, "max_uses", 0) or 0)
    if max_uses > 0 and used_count >= max_uses:
        return None

    if consume:
        row.used_count = used_count + 1
        db.add(row)
    return row


def find_signup_code_by_id(
    db: Session,
    *,
    org_slug: str,
    code_id: str,
    consume: bool = False,
    now: Optional[int] = None,
) -> Optional[SignupCode]:
    code_id = str(code_id or "").strip()
    if not code_id:
        return None

    query = select(SignupCode).where(
        SignupCode.id == code_id,
        SignupCode.org_slug == str(org_slug or "public").strip(),
        SignupCode.active.is_(True),
    )
    if consume:
        query = query.with_for_update()

    row = db.execute(query).scalar_one_or_none()
    if row is None:
        return None

    current = int(now or time.time())
    expires_at = int(getattr(row, "expires_at", 0) or 0)
    if expires_at and expires_at < current:
        return None

    used_count = int(getattr(row, "used_count", 0) or 0)
    max_uses = int(getattr(row, "max_uses", 0) or 0)
    if max_uses > 0 and used_count >= max_uses:
        return None

    if consume:
        row.used_count = used_count + 1
        db.add(row)
    return row


def issue_access_grant(
    *,
    code: SignupCode,
    org_slug: str,
    purpose: str,
    user_agent: str,
    now: Optional[int] = None,
    config: Optional[AccessGrantConfig] = None,
) -> tuple[str, dict[str, Any]]:
    cfg = config or load_access_grant_config(require_signing_key=True)
    purpose = normalize_purpose(purpose)
    issued_at = int(now or time.time())
    payload: dict[str, Any] = {
        "v": 1,
        "typ": "orkio_access_grant",
        "org": str(org_slug or "public").strip(),
        "purpose": purpose,
        "scope": _scope_for_code(code, purpose),
        "code_id": str(getattr(code, "id", "") or ""),
        "iat": issued_at,
        "exp": issued_at + cfg.ttl_seconds,
        "jti": secrets.token_urlsafe(18),
    }
    if cfg.bind_user_agent:
        payload["uah"] = _ua_hash(user_agent)

    payload_segment = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signature = hmac.new(
        cfg.signing_key.encode("utf-8"),
        payload_segment.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{payload_segment}.{_b64url_encode(signature)}", payload


def decode_access_grant(
    token: str,
    *,
    expected_org: Optional[str] = None,
    user_agent: str = "",
    now: Optional[int] = None,
    config: Optional[AccessGrantConfig] = None,
) -> dict[str, Any]:
    cfg = config or load_access_grant_config(require_signing_key=True)
    try:
        payload_segment, signature_segment = str(token or "").split(".", 1)
        supplied_signature = _b64url_decode(signature_segment)
    except Exception as exc:
        raise AccessGrantInvalidError("malformed_access_grant") from exc

    expected_signature = hmac.new(
        cfg.signing_key.encode("utf-8"),
        payload_segment.encode("ascii"),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(supplied_signature, expected_signature):
        raise AccessGrantInvalidError("invalid_access_grant_signature")

    try:
        payload = json.loads(_b64url_decode(payload_segment).decode("utf-8"))
    except Exception as exc:
        raise AccessGrantInvalidError("invalid_access_grant_payload") from exc

    current = int(now or time.time())
    if payload.get("typ") != "orkio_access_grant" or int(payload.get("v") or 0) != 1:
        raise AccessGrantInvalidError("unsupported_access_grant")
    if int(payload.get("exp") or 0) <= current:
        raise AccessGrantInvalidError("access_grant_expired")
    if int(payload.get("iat") or 0) > current + 60:
        raise AccessGrantInvalidError("access_grant_issued_in_future")

    purpose = normalize_purpose(payload.get("purpose"))
    payload["purpose"] = purpose

    if expected_org is not None:
        expected = str(expected_org or "public").strip()
        if str(payload.get("org") or "").strip() != expected:
            raise AccessGrantInvalidError("access_grant_tenant_mismatch")

    if cfg.bind_user_agent:
        if not hmac.compare_digest(
            str(payload.get("uah") or ""),
            _ua_hash(user_agent),
        ):
            raise AccessGrantInvalidError("access_grant_user_agent_mismatch")

    if not str(payload.get("code_id") or "").strip():
        raise AccessGrantInvalidError("access_grant_missing_code_id")
    return payload


def get_request_access_grant(
    request: Request,
    *,
    expected_org: Optional[str] = None,
    required: bool = True,
) -> Optional[dict[str, Any]]:
    cfg = load_access_grant_config(require_signing_key=required)
    token = request.cookies.get(cfg.cookie_name)
    if not token:
        if required:
            raise HTTPException(status_code=403, detail="ACCESS_GRANT_REQUIRED")
        return None
    try:
        return decode_access_grant(
            token,
            expected_org=expected_org,
            user_agent=request.headers.get("user-agent", ""),
            config=cfg,
        )
    except AccessGrantInvalidError as exc:
        if required:
            raise HTTPException(status_code=403, detail=str(exc))
        return None


def require_request_access_grant(
    request: Request,
    *,
    expected_org: str,
    db: Optional[Session] = None,
) -> dict[str, Any]:
    claims = get_request_access_grant(
        request,
        expected_org=expected_org,
        required=True,
    )
    if db is not None:
        row = find_signup_code_by_id(
            db,
            org_slug=expected_org,
            code_id=str(claims.get("code_id") or ""),
            consume=False,
        )
        if row is None:
            raise HTTPException(status_code=403, detail="ACCESS_GRANT_REVOKED")
    return claims


def set_access_grant_cookie(response: Any, token: str, config: AccessGrantConfig) -> None:
    response.set_cookie(
        key=config.cookie_name,
        value=token,
        max_age=config.ttl_seconds,
        expires=config.ttl_seconds,
        path="/",
        secure=config.cookie_secure,
        httponly=True,
        samesite=config.cookie_samesite,
    )


def clear_access_grant_cookie(response: Any, config: AccessGrantConfig) -> None:
    response.delete_cookie(
        key=config.cookie_name,
        path="/",
        secure=config.cookie_secure,
        httponly=True,
        samesite=config.cookie_samesite,
    )
