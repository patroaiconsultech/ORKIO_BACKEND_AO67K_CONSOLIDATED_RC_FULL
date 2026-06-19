# ORKIO_RTB06_REALTIME_FINALS_MESSAGES_BRIDGE
# Backend-only PATCH_MINIMUM for routes/realtime.py
#
# Purpose:
# - Preserve existing Realtime endpoints.
# - Inject recent thread context into Realtime instructions for every authenticated
#   user who is authorized to access the thread.
# - Inject Founder/CEO identity only for the two explicit founder admin emails:
#   daniel@patroai.com and dangraebin@gmail.com
# - Fail open: if context loading fails, Realtime still starts.

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

try:
    from sqlalchemy import select  # type: ignore
except Exception:  # pragma: no cover
    select = None  # type: ignore


try:
    from app.runtime.realtime_support import (  # type: ignore
        RealtimeClientSecretReq,
        RealtimeStartReq,
        RealtimeEventIn,
        RealtimeEndReq,
        RealtimeGuardReq,
        normalize_realtime_voice,
    )
except Exception:  # pragma: no cover
    class RealtimeClientSecretReq(BaseModel):
        model: Optional[str] = None
        voice: Optional[str] = None
        ttl_seconds: Optional[int] = 120
        mode: Optional[str] = None
        response_profile: Optional[str] = None
        language_profile: Optional[str] = None
        language: Optional[str] = None
        agent_id: Optional[str] = None
        thread_id: Optional[str] = None

    class RealtimeStartReq(BaseModel):
        agent_id: Optional[str] = None
        thread_id: Optional[str] = None
        voice: Optional[str] = None
        model: Optional[str] = None
        ttl_seconds: Optional[int] = 120
        mode: Optional[str] = None
        response_profile: Optional[str] = None
        language_profile: Optional[str] = None
        language: Optional[str] = None

    class RealtimeEventIn(BaseModel):
        name: Optional[str] = None
        event: Optional[str] = None
        type: Optional[str] = None
        meta: Optional[Dict[str, Any]] = None
        payload: Optional[Dict[str, Any]] = None
        ts: Optional[Any] = None

    class RealtimeEndReq(BaseModel):
        session_id: Optional[str] = None
        reason: Optional[str] = None
        meta: Optional[Dict[str, Any]] = None

    class RealtimeGuardReq(BaseModel):
        thread_id: Optional[str] = None
        message: Optional[str] = None

    def normalize_realtime_voice(raw: Any, default: str = "cedar") -> str:
        voice = str(raw or "").strip().lower()
        allowed = {
            "alloy",
            "ash",
            "ballad",
            "cedar",
            "coral",
            "echo",
            "fable",
            "marin",
            "nova",
            "onyx",
            "sage",
            "shimmer",
            "verse",
        }
        aliases = {"marine": "marin"}
        voice = aliases.get(voice, voice)
        return voice if voice in allowed else default


try:
    from app.runtime.realtime_session_builder import (  # type: ignore
        build_openai_realtime_client_secret_payload,
        realtime_session_debug_snapshot,
    )
except Exception:  # pragma: no cover
    build_openai_realtime_client_secret_payload = None  # type: ignore

    def realtime_session_debug_snapshot(payload: Dict[str, Any]) -> Dict[str, Any]:
        session = payload.get("session") if isinstance(payload, dict) else {}
        session = session if isinstance(session, dict) else {}
        audio = session.get("audio") if isinstance(session, dict) else {}
        audio = audio if isinstance(audio, dict) else {}
        output = audio.get("output") if isinstance(audio, dict) else {}
        output = output if isinstance(output, dict) else {}
        return {
            "has_payload": bool(payload),
            "model": payload.get("model") or session.get("model"),
            "voice": payload.get("voice") or output.get("voice"),
            "has_instructions": bool(session.get("instructions") or payload.get("instructions")),
        }


class RealtimeEventsBatchReq(BaseModel):
    session_id: str
    events: List[RealtimeEventIn] = []


def _now_ts() -> int:
    return int(time.time())


def _new_id(prefix: str = "rt") -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _positive_int_env(name: str, default: int) -> int:
    try:
        value = int(str(os.getenv(name, str(default))).strip())
        return value if value > 0 else default
    except Exception:
        return default


REALTIME_PUBLIC_BETA_MAX_SECONDS = _positive_int_env(
    "ORKIO_REALTIME_PUBLIC_BETA_MAX_SECONDS",
    120,
)
REALTIME_PUBLIC_BETA_COOLDOWN_SECONDS = _positive_int_env(
    "ORKIO_REALTIME_PUBLIC_BETA_COOLDOWN_SECONDS",
    600,
)
REALTIME_ADVISORY_RECOMMENDED_SECONDS = _positive_int_env(
    "ORKIO_REALTIME_ADVISORY_RECOMMENDED_SECONDS",
    120,
)
REALTIME_CLIENT_SECRET_TTL_SECONDS = _positive_int_env(
    "ORKIO_REALTIME_CLIENT_SECRET_TTL_SECONDS",
    3600,
)
REALTIME_THREAD_CONTEXT_LIMIT = _positive_int_env(
    "ORKIO_REALTIME_THREAD_CONTEXT_LIMIT",
    18,
)
REALTIME_THREAD_CONTEXT_MAX_CHARS = _positive_int_env(
    "ORKIO_REALTIME_THREAD_CONTEXT_MAX_CHARS",
    6000,
)

FOUNDER_ADMIN_EMAILS = {
    "daniel@patroai.com",
    "dangraebin@gmail.com",
}


def _safe_getattr(obj: Any, name: str, default: Any = None) -> Any:
    try:
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)
    except Exception:
        return default


def _json_safe(value: Any) -> Any:
    """Convert SDK/Pydantic/SQLAlchemy-ish objects into JSON-safe primitives."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v) for v in value]

    for method_name in ("model_dump", "dict"):
        method = getattr(value, method_name, None)
        if callable(method):
            try:
                if method_name == "model_dump":
                    return _json_safe(method(mode="json"))
                return _json_safe(method())
            except Exception:
                pass

    method = getattr(value, "to_dict", None)
    if callable(method):
        try:
            return _json_safe(method())
        except Exception:
            pass

    method = getattr(value, "to_json", None)
    if callable(method):
        try:
            return _json_safe(json.loads(method()))
        except Exception:
            pass

    try:
        attrs = {
            str(k): _json_safe(v)
            for k, v in vars(value).items()
            if not str(k).startswith("_")
        }
        if attrs:
            return attrs
    except Exception:
        pass

    return str(value)


def _json_response(payload: Dict[str, Any], status_code: int = 200) -> JSONResponse:
    return JSONResponse(content=_json_safe(payload), status_code=status_code)


def _build_esg_usage_advisory() -> Dict[str, Any]:
    recommended = max(30, int(REALTIME_ADVISORY_RECOMMENDED_SECONDS or 120))
    return {
        "enabled": True,
        "mode": "advisory_only",
        "recommended_seconds": recommended,
        "hard_limit_enforced": False,
        "cooldown_enforced": False,
        "title": "Uso consciente da voz em tempo real",
        "message": (
            "Para economizar créditos, dados móveis, bateria e energia, recomendamos "
            f"sessões de voz objetivas de até {recommended} segundos quando possível. "
            "A conversa não será interrompida automaticamente por essa recomendação."
        ),
        "esg": {
            "cost_efficiency": True,
            "data_saving": True,
            "battery_saving": True,
            "energy_saving": True,
        },
    }


def _normalize_email(value: Any) -> str:
    return str(value or "").strip().lower()


def _user_email_candidates(user: Any, db_user: Any = None) -> List[str]:
    values: List[str] = []
    for source in (user, db_user):
        for key in (
            "email",
            "user_email",
            "preferred_username",
            "login",
            "username",
            "upn",
        ):
            raw = _normalize_email(_safe_getattr(source, key, ""))
            if raw and "@" in raw and raw not in values:
                values.append(raw)

    # Some auth payloads keep email inside nested claims/profile dictionaries.
    for source in (user, db_user):
        for key in ("claims", "profile", "raw", "payload"):
            nested = _safe_getattr(source, key, None)
            if isinstance(nested, dict):
                for nested_key in ("email", "user_email", "preferred_username", "upn"):
                    raw = _normalize_email(nested.get(nested_key))
                    if raw and "@" in raw and raw not in values:
                        values.append(raw)

    return values


def _is_daniel_founder_identity(user: Any, db_user: Any = None) -> bool:
    """Strict Founder/Admin identity guard.

    This intentionally checks only authenticated email claims.
    It does not grant founder identity by display name, org, role or user_id.
    """

    emails = set(_user_email_candidates(user, db_user))
    return bool(emails.intersection(FOUNDER_ADMIN_EMAILS))


def _is_admin_user(user: Any, db_user: Any = None) -> bool:
    roles = {"admin", "owner", "superadmin", "super_admin", "founder", "dev", "developer"}
    user_role = str(_safe_getattr(user, "role", "") or "").strip().lower()
    db_role = str(_safe_getattr(db_user, "role", "") or "").strip().lower()
    user_scope = str(_safe_getattr(user, "scope", "") or "").strip().lower()
    db_scope = str(_safe_getattr(db_user, "scope", "") or "").strip().lower()

    user_email = _normalize_email(_safe_getattr(user, "email", "") or _safe_getattr(user, "user_email", ""))
    db_email = _normalize_email(_safe_getattr(db_user, "email", "") or _safe_getattr(db_user, "user_email", ""))

    admin_email_env = ",".join(
        [
            os.getenv("ORKIO_SUPER_ADMIN_EMAILS", ""),
            os.getenv("ORKIO_ADMIN_EMAILS", ""),
            os.getenv("SUPER_ADMIN_EMAILS", ""),
            os.getenv("ADMIN_EMAILS", ""),
            os.getenv("VITE_ADMIN_EMAILS", ""),
            "daniel@patroai.com",
            "dangraebin@gmail.com",
        ]
    )
    admin_emails = {item.strip().lower() for item in admin_email_env.split(",") if item.strip()}

    return bool(
        user_role in roles
        or db_role in roles
        or user_scope in {"internal", "staff", "admin", "superadmin", "super_admin"}
        or db_scope in {"internal", "staff", "admin", "superadmin", "super_admin"}
        or bool(_safe_getattr(user, "is_admin", False))
        or bool(_safe_getattr(user, "admin", False))
        or bool(_safe_getattr(user, "super_admin", False))
        or bool(_safe_getattr(user, "is_super_admin", False))
        or bool(_safe_getattr(db_user, "is_admin", False))
        or bool(_safe_getattr(db_user, "admin", False))
        or bool(_safe_getattr(db_user, "super_admin", False))
        or bool(_safe_getattr(db_user, "is_super_admin", False))
        or (user_email and user_email in admin_emails)
        or (db_email and db_email in admin_emails)
    )


def _default_current_user() -> Dict[str, Any]:
    raise HTTPException(status_code=401, detail="Not authenticated")


def _default_db() -> None:
    return None


def _resolve_org_safe(deps: SimpleNamespace, user: Any, x_org_slug: Optional[str]) -> str:
    resolver = getattr(deps, "_resolve_org", None)
    if callable(resolver):
        try:
            return str(resolver(user, x_org_slug) or "public")
        except Exception:
            pass

    org = (
        x_org_slug
        or _safe_getattr(user, "org_slug", None)
        or _safe_getattr(user, "org", None)
        or "public"
    )
    return str(org or "public").strip() or "public"


def _lookup_db_user(deps: SimpleNamespace, db: Any, user: Any, org: str) -> Any:
    User = getattr(deps, "User", None)
    uid = _safe_getattr(user, "sub", None) or _safe_getattr(user, "id", None)

    if db is None or User is None or select is None or not uid:
        return None

    try:
        return (
            db.execute(
                select(User).where(
                    User.id == uid,
                    User.org_slug == org,
                )
            )
            .scalar_one_or_none()
        )
    except Exception:
        return None


def _call_thread_access_helper(
    helper: Any,
    db: Any,
    org: str,
    thread_id: str,
    uid: Optional[str],
) -> Tuple[bool, Optional[str]]:
    if not callable(helper):
        return False, "helper_not_callable"

    call_patterns = (
        (db, org, thread_id, uid),
        (db, org, thread_id),
        (db, thread_id, uid),
        (thread_id, uid),
    )
    for args in call_patterns:
        try:
            helper(*args)
            return True, None
        except TypeError:
            continue
        except HTTPException as exc:
            return False, f"http_{exc.status_code}"
        except Exception as exc:
            return False, str(exc)[:120] or "helper_error"

    return False, "signature_mismatch"


def _thread_access_allowed(
    deps: SimpleNamespace,
    db: Any,
    *,
    org: str,
    thread_id: str,
    uid: Optional[str],
    user: Any,
    db_user: Any,
) -> bool:
    """Return True only when the current authenticated user can read the thread."""

    if not thread_id:
        return False

    if _is_admin_user(user, db_user):
        return True

    for helper_name in ("_require_thread_member", "_ensure_thread_owner"):
        ok, reason = _call_thread_access_helper(
            getattr(deps, helper_name, None),
            db,
            org,
            thread_id,
            uid,
        )
        if ok:
            return True
        # If a helper explicitly denies with HTTP 403/404, fail closed.
        if reason in {"http_403", "http_404"}:
            return False

    Thread = getattr(deps, "Thread", None)
    if db is None or Thread is None or select is None or not uid:
        return False

    try:
        thread = (
            db.execute(
                select(Thread).where(
                    Thread.id == thread_id,
                    Thread.org_slug == org,
                )
            )
            .scalar_one_or_none()
        )
        if not thread:
            return False

        owner_id = (
            _safe_getattr(thread, "user_id", None)
            or _safe_getattr(thread, "owner_id", None)
            or _safe_getattr(thread, "created_by", None)
        )
        return bool(owner_id and str(owner_id) == str(uid))
    except Exception:
        return False


def _message_content(message: Any) -> str:
    candidates = (
        _safe_getattr(message, "content", None),
        _safe_getattr(message, "text", None),
        _safe_getattr(message, "message", None),
        _safe_getattr(message, "transcript_punct", None),
        _safe_getattr(message, "transcript_raw", None),
    )
    for item in candidates:
        text = str(item or "").strip()
        if text:
            return text
    return ""


def _message_role(message: Any) -> str:
    role = str(
        _safe_getattr(message, "role", None)
        or _safe_getattr(message, "speaker_type", None)
        or "user"
    ).strip().lower()

    if role in {"assistant", "agent", "ai", "orkio"}:
        return "assistant"
    if role in {"system", "developer"}:
        return "system"
    return "user"


def _message_label(message: Any) -> str:
    role = _message_role(message)
    if role == "assistant":
        agent_name = str(_safe_getattr(message, "agent_name", "") or "").strip()
        return agent_name or "Orkio"
    if role == "system":
        return "Sistema"
    user_name = str(_safe_getattr(message, "user_name", "") or "").strip()
    return user_name or "Usuário"


def _sanitize_context_text(value: Any, *, max_chars: int = 900) -> str:
    text = " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())
    if not text:
        return ""
    # Avoid injecting obvious secrets into Realtime instructions.
    forbidden_markers = (
        "bearer ",
        "authorization:",
        "api_key",
        "apikey",
        "secret=",
        "password=",
        "token=",
        "set-cookie",
        "cookie:",
    )
    lowered = text.lower()
    if any(marker in lowered for marker in forbidden_markers):
        return "[conteúdo omitido por segurança]"
    if len(text) > max_chars:
        return text[: max_chars - 1].rstrip() + "…"
    return text


def _load_recent_thread_messages(
    deps: SimpleNamespace,
    db: Any,
    *,
    org: str,
    thread_id: str,
    limit: int,
) -> List[Any]:
    Message = getattr(deps, "Message", None)
    if db is None or Message is None or select is None or not thread_id:
        return []

    safe_limit = max(1, min(int(limit or 18), 24))

    try:
        rows = (
            db.execute(
                select(Message)
                .where(
                    Message.org_slug == org,
                    Message.thread_id == thread_id,
                )
                .order_by(Message.created_at.desc(), Message.id.desc())
                .limit(safe_limit)
            )
            .scalars()
            .all()
        )
        return list(reversed(list(rows or [])))
    except Exception:
        # Some DB models may not support id desc ordering.
        try:
            rows = (
                db.execute(
                    select(Message)
                    .where(
                        Message.org_slug == org,
                        Message.thread_id == thread_id,
                    )
                    .order_by(Message.created_at.desc())
                    .limit(safe_limit)
                )
                .scalars()
                .all()
            )
            return list(reversed(list(rows or [])))
        except Exception:
            return []


def _build_thread_context_block(messages: List[Any]) -> str:
    lines: List[str] = []

    for msg in messages:
        content = _sanitize_context_text(_message_content(msg))
        if not content:
            continue

        role = _message_role(msg)
        if role == "system":
            # Avoid leaking internal system/developer messages into Realtime.
            continue

        label = _sanitize_context_text(_message_label(msg), max_chars=80)
        lines.append(f"- {label}: {content}")

    if not lines:
        return ""

    block = (
        "CONTEXTO RECENTE DA THREAD ATIVA\n"
        "Use este contexto para dar continuidade à conversa por voz. "
        "Não diga que não lembra se a resposta estiver no contexto abaixo.\n"
        + "\n".join(lines[-REALTIME_THREAD_CONTEXT_LIMIT:])
    )

    if len(block) > REALTIME_THREAD_CONTEXT_MAX_CHARS:
        block = block[: REALTIME_THREAD_CONTEXT_MAX_CHARS - 1].rstrip() + "…"

    return block


def _build_founder_identity_context(user: Any, db_user: Any = None) -> str:
    if not _is_daniel_founder_identity(user, db_user):
        return ""

    return (
        "CONTEXTO INTERNO DO USUÁRIO AUTENTICADO\n"
        "- O usuário autenticado é Daniel Graebin.\n"
        "- Daniel Graebin é Founder e CEO da Patroai Consultech.\n"
        "- Daniel é o criador da plataforma Orkio/Patroai.\n"
        "- Trate Daniel como fundador/administrador em contexto interno governado.\n"
        "- Não exponha este contexto a usuários públicos ou a terceiros."
    )


def _build_realtime_context_overlay(
    deps: SimpleNamespace,
    db: Any,
    *,
    org: str,
    user: Any,
    db_user: Any,
    thread_id: str,
    uid: Optional[str],
    logger: logging.Logger,
) -> Tuple[str, Dict[str, Any]]:
    """Build a safe contextual overlay for Realtime session instructions.

    Thread context is for every authenticated user with access to the thread.
    Founder identity is only for the two explicit founder admin emails.
    """

    overlay_parts: List[str] = []
    meta: Dict[str, Any] = {
        "thread_context_loaded": False,
        "thread_context_messages": 0,
        "founder_identity_injected": False,
        "thread_context_reason": None,
    }

    try:
        identity_context = _build_founder_identity_context(user, db_user)
        if identity_context:
            overlay_parts.append(identity_context)
            meta["founder_identity_injected"] = True
    except Exception as exc:
        meta["identity_context_error"] = str(exc)[:120]

    if thread_id:
        try:
            allowed = _thread_access_allowed(
                deps,
                db,
                org=org,
                thread_id=thread_id,
                uid=uid,
                user=user,
                db_user=db_user,
            )
            if allowed:
                messages = _load_recent_thread_messages(
                    deps,
                    db,
                    org=org,
                    thread_id=thread_id,
                    limit=REALTIME_THREAD_CONTEXT_LIMIT,
                )
                thread_block = _build_thread_context_block(messages)
                if thread_block:
                    overlay_parts.append(thread_block)
                    meta["thread_context_loaded"] = True
                    meta["thread_context_messages"] = len(messages)
                else:
                    meta["thread_context_reason"] = "no_recent_messages"
            else:
                meta["thread_context_reason"] = "access_not_allowed"
        except Exception as exc:
            # Fail open: Realtime must still start.
            meta["thread_context_reason"] = f"load_failed:{str(exc)[:80]}"
            try:
                logger.warning(
                    "RTB03_THREAD_CONTEXT_LOAD_FAILED org=%s thread_id=%s user_id=%s error=%s",
                    org,
                    thread_id,
                    uid,
                    str(exc),
                )
            except Exception:
                pass

    if not overlay_parts:
        return "", meta

    overlay = (
        "RTB-03 — PONTE DE CONTEXTO REALTIME\n"
        "As informações abaixo foram carregadas de forma autorizada no início da sessão de voz.\n\n"
        + "\n\n".join(overlay_parts)
        + "\n\nINSTRUÇÃO DE CONTINUIDADE\n"
        "- Se o usuário perguntar se você lembra, responda usando o contexto recente acima.\n"
        "- Se algo não estiver no contexto, diga com honestidade que não tem esse detalhe na sessão atual.\n"
        "- Não invente fatos não presentes no contexto."
    )

    return overlay, meta


def _append_instruction_overlay(base_instructions: str, overlay: str) -> str:
    base = str(base_instructions or "").strip()
    if not overlay:
        return base
    if not base:
        return overlay
    return f"{base}\n\n{overlay}"


def _build_basic_realtime_payload(
    *,
    model: Optional[str],
    voice: Optional[str],
    ttl_seconds: Optional[int],
    instructions: Optional[str],
    resolved_language: Optional[str],
) -> Dict[str, Any]:
    selected_model = (
        str(model or "").strip()
        or os.getenv("OPENAI_REALTIME_MODEL", "").strip()
        or "gpt-4o-realtime-preview"
    )

    selected_voice = normalize_realtime_voice(
        voice or os.getenv("OPENAI_REALTIME_VOICE_DEFAULT", "cedar"),
        default=os.getenv("OPENAI_REALTIME_VOICE_DEFAULT", "cedar"),
    )

    ttl = max(10, min(7200, int(ttl_seconds or 120)))
    language = str(resolved_language or "pt").strip().lower() or "pt"

    return {
        "expires_after": {
            "anchor": "created_at",
            "seconds": ttl,
        },
        "session": {
            "type": "realtime",
            "model": selected_model,
            "instructions": instructions
            or (
                "Você é Orkio, agente executivo da plataforma PatroAI. "
                "Responda em português do Brasil, com objetividade e segurança."
            ),
            "output_modalities": ["audio"],
            "audio": {
                "output": {
                    "voice": selected_voice,
                },
                "input": {
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.72,
                        "prefix_padding_ms": 500,
                        "silence_duration_ms": 1800,
                        "create_response": True,
                        "interrupt_response": True,
                    },
                    "transcription": {
                        "model": "gpt-4o-mini-transcribe",
                        "language": language,
                    },
                },
            },
        },
    }


def _payload_looks_ga_compatible(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False

    session = payload.get("session")
    if not isinstance(session, dict):
        return False

    audio = session.get("audio")
    if not isinstance(audio, dict):
        return False

    audio_input = audio.get("input")
    audio_output = audio.get("output")
    if not isinstance(audio_input, dict) or not isinstance(audio_output, dict):
        return False

    if not audio_output.get("voice"):
        return False

    if not isinstance(audio_input.get("turn_detection"), dict):
        return False

    if not isinstance(payload.get("expires_after"), dict):
        return False

    return True


def _normalize_realtime_payload_for_ga(
    payload: Any,
    *,
    model: Optional[str],
    voice: Optional[str],
    ttl_seconds: Optional[int],
    instructions: Optional[str],
    resolved_language: Optional[str],
) -> Dict[str, Any]:
    if _payload_looks_ga_compatible(payload):
        # Ensure patched instructions are not dropped by a stale builder.
        try:
            session = payload.get("session")
            if isinstance(session, dict) and instructions:
                session["instructions"] = instructions
        except Exception:
            pass
        return payload

    return _build_basic_realtime_payload(
        model=model,
        voice=voice,
        ttl_seconds=ttl_seconds,
        instructions=instructions,
        resolved_language=resolved_language,
    )


def _extract_secret_value(secret_obj: Any) -> Tuple[Optional[str], Any]:
    if secret_obj is None:
        return None, None

    safe_obj = _json_safe(secret_obj)

    if isinstance(safe_obj, dict):
        client_secret = (
            safe_obj.get("client_secret")
            if isinstance(safe_obj.get("client_secret"), dict)
            else {}
        )
        return (
            safe_obj.get("value")
            or client_secret.get("value")
            or safe_obj.get("secret")
            or safe_obj.get("client_secret_value"),
            safe_obj.get("session"),
        )

    value = getattr(secret_obj, "value", None)
    session = getattr(secret_obj, "session", None)
    return value, _json_safe(session)


def _build_instructions(
    deps: SimpleNamespace,
    *,
    mode: str,
    response_profile: str,
    language_profile: str,
) -> str:
    builder = getattr(deps, "build_summit_instructions", None)
    sensitive_guard = getattr(deps, "_sensitive_guard_instruction", None)

    instructions = ""

    if callable(builder):
        try:
            instructions = str(
                builder(
                    mode=mode,
                    agent_instructions=(
                        "IDENTIDADE OBRIGATÓRIA DO REALTIME\n"
                        "- Você é Orkio, agente da plataforma PatroAI.\n"
                        "- Responda sempre em português do Brasil.\n"
                        "- Seja claro, executivo, útil e seguro.\n"
                    ),
                    language_profile=language_profile,
                    response_profile=response_profile,
                )
                or ""
            ).strip()
        except Exception:
            instructions = ""

    if not instructions:
        instructions = (
            "Você é Orkio, agente executivo da plataforma PatroAI. "
            "Responda sempre em português do Brasil, com clareza, objetividade e segurança."
        )

    if callable(sensitive_guard):
        try:
            guard = str(sensitive_guard() or "").strip()
            if guard:
                instructions = f"{instructions}\n\n{guard}"
        except Exception:
            pass

    return instructions


async def _mint_client_secret(
    deps: SimpleNamespace,
    body: Any,
    *,
    instructions: str,
    resolved_language: str,
    summit_runtime: bool = False,
    logger: logging.Logger,
) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")

    model = str(_safe_getattr(body, "model", "") or "").strip() or None
    voice = normalize_realtime_voice(
        _safe_getattr(body, "voice", None)
        or os.getenv("OPENAI_REALTIME_VOICE_DEFAULT", "cedar"),
        default=os.getenv("OPENAI_REALTIME_VOICE_DEFAULT", "cedar"),
    )
    ttl_seconds = int(_safe_getattr(body, "ttl_seconds", None) or REALTIME_PUBLIC_BETA_MAX_SECONDS)

    payload: Dict[str, Any]
    if callable(build_openai_realtime_client_secret_payload):
        try:
            payload = build_openai_realtime_client_secret_payload(
                ttl_seconds=ttl_seconds,
                model=model,
                voice=voice,
                instructions=instructions,
                resolved_language=resolved_language,
                summit_runtime=summit_runtime,
            )
        except Exception:
            payload = _build_basic_realtime_payload(
                model=model,
                voice=voice,
                ttl_seconds=ttl_seconds,
                instructions=instructions,
                resolved_language=resolved_language,
            )
    else:
        payload = _build_basic_realtime_payload(
            model=model,
            voice=voice,
            ttl_seconds=ttl_seconds,
            instructions=instructions,
            resolved_language=resolved_language,
        )

    payload = _normalize_realtime_payload_for_ga(
        payload,
        model=model,
        voice=voice,
        ttl_seconds=ttl_seconds,
        instructions=instructions,
        resolved_language=resolved_language,
    )

    try:
        logger.warning(
            "RTB03_REALTIME_CLIENT_SECRET_PAYLOAD %s",
            json.dumps(realtime_session_debug_snapshot(payload), ensure_ascii=False, sort_keys=True),
        )
    except Exception:
        pass

    OpenAI = getattr(deps, "OpenAI", None)
    if OpenAI is not None:
        try:
            client = OpenAI(api_key=api_key)
            secret_obj = client.realtime.client_secrets.create(**payload)  # type: ignore[attr-defined]
            value, session = _extract_secret_value(secret_obj)
            if value:
                return {"value": value, "session": session}
        except Exception as sdk_err:
            try:
                logger.warning("RTB03_REALTIME_SDK_SECRET_FAILED %s", sdk_err)
            except Exception:
                pass

    try:
        import urllib.request

        req = urllib.request.Request(
            "https://api.openai.com/v1/realtime/client_secrets",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            value, session = _extract_secret_value(data)
            if not value:
                raise RuntimeError("Realtime client secret missing in REST response")
            return {"value": value, "session": session, "sdk_fallback": True}
    except Exception as rest_err:
        try:
            logger.exception("RTB03_REALTIME_REST_SECRET_FAILED %s", rest_err)
        except Exception:
            pass

    raise HTTPException(status_code=502, detail="Failed to mint Realtime client secret")


def _maybe_persist_realtime_session(
    deps: SimpleNamespace,
    db: Any,
    *,
    session_id: str,
    org: str,
    user_id: Optional[str],
    thread_id: Optional[str],
    started_at: int,
    mode: str,
    agent_id: Optional[str] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    RealtimeSession = getattr(deps, "RealtimeSession", None)
    if db is None or RealtimeSession is None:
        return

    try:
        rs = RealtimeSession()
        values = {
            "id": session_id,
            "org_slug": org,
            "user_id": user_id,
            "thread_id": thread_id,
            "agent_id": agent_id,
            "started_at": started_at,
            "mode": mode,
            "status": "active",
        }
        if meta is not None:
            values["meta"] = json.dumps(meta, ensure_ascii=False)

        for key, value in values.items():
            try:
                setattr(rs, key, value)
            except Exception:
                pass

        db.add(rs)
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass


def _maybe_mark_realtime_session_ended(
    deps: SimpleNamespace,
    db: Any,
    *,
    session_id: Optional[str],
    ended_at: int,
    reason: Optional[str],
) -> bool:
    if not session_id:
        return False

    RealtimeSession = getattr(deps, "RealtimeSession", None)
    if db is None or RealtimeSession is None or select is None:
        return False

    try:
        rs = (
            db.execute(select(RealtimeSession).where(RealtimeSession.id == session_id))
            .scalar_one_or_none()
        )
        if not rs:
            return False

        for key, value in {
            "ended_at": ended_at,
            "status": "ended",
            "end_reason": reason or "client_end",
            "reason": reason or "client_end",
        }.items():
            try:
                setattr(rs, key, value)
            except Exception:
                pass

        db.add(rs)
        db.commit()
        return True
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
        return False



# ORKIO_RTB06_REALTIME_FINALS_MESSAGES_BRIDGE
def _rtb06_event_dict(event: Any) -> Dict[str, Any]:
    data = _json_safe(event)
    return data if isinstance(data, dict) else {}


def _rtb06_collect_text_candidates(value: Any, depth: int = 0) -> List[str]:
    if value is None or depth > 5:
        return []

    if isinstance(value, (str, int, float)):
        text = str(value or "").strip()
        if not text:
            return []
        low = text.lower()
        if low in {"true", "false", "completed", "done", "ok", "success", "event"}:
            return []
        if low.startswith("telemetry."):
            return []
        return [text]

    if isinstance(value, list):
        out: List[str] = []
        for item in value:
            out.extend(_rtb06_collect_text_candidates(item, depth + 1))
        return out

    if not isinstance(value, dict):
        return []

    preferred_keys = (
        "transcript_punct",
        "transcript_text",
        "transcript",
        "input_transcript",
        "inputTranscript",
        "output_text",
        "outputText",
        "final_text",
        "finalText",
        "assistant_text",
        "assistantText",
        "text",
        "content",
        "message",
        "answer",
    )
    out: List[str] = []

    for key in preferred_keys:
        if key in value:
            out.extend(_rtb06_collect_text_candidates(value.get(key), depth + 1))

    nested_keys = (
        "payload",
        "meta",
        "data",
        "item",
        "event",
        "response",
        "message",
        "content",
        "delta",
        "output",
        "outputs",
        "transcript",
    )
    for key in nested_keys:
        nested = value.get(key)
        if isinstance(nested, (dict, list)):
            out.extend(_rtb06_collect_text_candidates(nested, depth + 1))

    return out


def _rtb06_extract_final_text(event: Any) -> str:
    texts = _rtb06_collect_text_candidates(_rtb06_event_dict(event))
    texts = [t for t in texts if len(t.strip()) >= 2]
    if not texts:
        return ""
    selected = max(texts, key=len)
    return _sanitize_context_text(selected, max_chars=8000)


def _rtb06_event_hash(session_id: str, event_name: str, role: str, text: str) -> str:
    raw = f"{session_id}|{event_name}|{role}|{text}".encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()


def _rtb06_get_session_context(
    deps: SimpleNamespace,
    db: Any,
    *,
    session_id: str,
    fallback_org: str,
    fallback_user_id: Optional[str],
) -> Dict[str, Any]:
    context: Dict[str, Any] = {
        "org": fallback_org or "public",
        "user_id": fallback_user_id,
        "thread_id": None,
        "agent_id": None,
        "found": False,
    }
    RealtimeSession = getattr(deps, "RealtimeSession", None)
    if db is None or RealtimeSession is None or select is None or not session_id:
        return context

    try:
        rs = (
            db.execute(select(RealtimeSession).where(RealtimeSession.id == session_id))
            .scalar_one_or_none()
        )
        if not rs:
            return context
        context["found"] = True
        context["org"] = str(_safe_getattr(rs, "org_slug", None) or context["org"] or "public")
        context["user_id"] = str(_safe_getattr(rs, "user_id", None) or context["user_id"] or "") or None
        context["thread_id"] = str(_safe_getattr(rs, "thread_id", None) or "") or None
        context["agent_id"] = str(_safe_getattr(rs, "agent_id", None) or "") or None
    except Exception:
        return context

    return context


def _rtb06_message_has_existing(
    deps: SimpleNamespace,
    db: Any,
    *,
    org: str,
    thread_id: str,
    role: str,
    text: str,
) -> bool:
    Message = getattr(deps, "Message", None)
    if db is None or Message is None or select is None or not thread_id or not text:
        return False

    try:
        query = select(Message).where(
            Message.org_slug == org,
            Message.thread_id == thread_id,
            Message.role == role,
            Message.content == text,
        ).limit(1)
        return bool(db.execute(query).scalar_one_or_none())
    except Exception:
        return False


def _rtb06_set_if_possible(obj: Any, key: str, value: Any) -> None:
    try:
        setattr(obj, key, value)
    except Exception:
        pass


def _rtb06_create_message_instance(
    Message: Any,
    *,
    message_id: str,
    org: str,
    thread_id: str,
    user_id: Optional[str],
    role: str,
    content: str,
    agent_name: Optional[str],
    event_hash: str,
    session_id: str,
    event_name: str,
) -> Any:
    msg = Message()
    now = datetime.now(timezone.utc)
    metadata_json = json.dumps(
        {
            "source": "realtime",
            "patch": "RTB06",
            "realtime_session_id": session_id,
            "event_name": event_name,
            "event_hash": event_hash,
        },
        ensure_ascii=False,
    )

    values = {
        "id": message_id,
        "org_slug": org,
        "thread_id": thread_id,
        "user_id": user_id,
        "role": role,
        "content": content,
        "text": content,
        "message": content,
        "agent_name": agent_name if role == "assistant" else None,
        "speaker_name": agent_name if role == "assistant" else None,
        "created_at": now,
        "updated_at": now,
        "source": "realtime",
        "channel": "realtime",
        "realtime_session_id": session_id,
        "idempotency_key": event_hash,
        "client_event_id": event_hash,
        "metadata": metadata_json,
        "meta": metadata_json,
    }

    for key, value in values.items():
        if value is not None:
            _rtb06_set_if_possible(msg, key, value)

    return msg


def _rtb06_insert_message(
    deps: SimpleNamespace,
    db: Any,
    *,
    org: str,
    thread_id: str,
    user_id: Optional[str],
    role: str,
    content: str,
    agent_name: Optional[str],
    session_id: str,
    event_name: str,
    event_hash: str,
) -> bool:
    Message = getattr(deps, "Message", None)
    if db is None or Message is None or not thread_id or not content:
        return False

    if _rtb06_message_has_existing(
        deps,
        db,
        org=org,
        thread_id=thread_id,
        role=role,
        text=content,
    ):
        return False

    def build_msg(use_epoch: bool = False) -> Any:
        msg = _rtb06_create_message_instance(
            Message,
            message_id=f"msg_rt_{uuid.uuid4().hex}",
            org=org,
            thread_id=thread_id,
            user_id=user_id,
            role=role,
            content=content,
            agent_name=agent_name,
            event_hash=event_hash,
            session_id=session_id,
            event_name=event_name,
        )
        if use_epoch:
            for key in ("created_at", "updated_at"):
                _rtb06_set_if_possible(msg, key, int(time.time()))
        return msg

    for use_epoch in (False, True):
        try:
            db.add(build_msg(use_epoch=use_epoch))
            db.commit()
            return True
        except Exception:
            try:
                db.rollback()
            except Exception:
                pass

    return False


def _rtb06_promote_realtime_finals_to_messages(
    deps: SimpleNamespace,
    db: Any,
    *,
    org: str,
    user_id: Optional[str],
    session_id: str,
    events: List[Any],
    logger: logging.Logger,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "attempted": 0,
        "inserted": 0,
        "skipped": 0,
        "thread_id": None,
    }

    if not events or not session_id:
        return result

    session_ctx = _rtb06_get_session_context(
        deps,
        db,
        session_id=session_id,
        fallback_org=org,
        fallback_user_id=user_id,
    )
    effective_org = str(session_ctx.get("org") or org or "public")
    effective_user_id = str(session_ctx.get("user_id") or user_id or "") or None
    thread_id = str(session_ctx.get("thread_id") or "") or None
    result["thread_id"] = thread_id

    if not thread_id:
        return result

    for ev in events:
        event_name = _event_name(ev).strip()
        event_key = event_name.lower()
        if event_key not in {"transcript.final", "response.final"}:
            continue

        role = "user" if event_key == "transcript.final" else "assistant"
        text = _rtb06_extract_final_text(ev)
        if not text:
            result["skipped"] += 1
            continue

        event_hash = _rtb06_event_hash(session_id, event_key, role, text)
        result["attempted"] += 1
        ok = _rtb06_insert_message(
            deps,
            db,
            org=effective_org,
            thread_id=thread_id,
            user_id=effective_user_id,
            role=role,
            content=text,
            agent_name=("Orkio" if role == "assistant" else None),
            session_id=session_id,
            event_name=event_key,
            event_hash=event_hash,
        )
        if ok:
            result["inserted"] += 1
        else:
            result["skipped"] += 1

    if result["attempted"]:
        try:
            logger.warning(
                "RTB06_REALTIME_FINALS_PROMOTION session_id=%s thread_id=%s attempted=%s inserted=%s skipped=%s",
                session_id,
                thread_id,
                result["attempted"],
                result["inserted"],
                result["skipped"],
            )
        except Exception:
            pass

    return result


def _event_name(event: Any) -> str:
    payload = _safe_getattr(event, "payload", {}) or {}
    meta = _safe_getattr(event, "meta", {}) or {}
    return str(
        _safe_getattr(event, "name", None)
        or _safe_getattr(event, "event", None)
        or _safe_getattr(event, "type", None)
        or (payload.get("event_type") if isinstance(payload, dict) else None)
        or (meta.get("event_type") if isinstance(meta, dict) else None)
        or "event"
    )


def build_realtime_router(deps: SimpleNamespace) -> APIRouter:
    """Build Realtime router using dependencies injected by app/main.py."""

    router = APIRouter()
    logger = getattr(deps, "logger", None) or logging.getLogger("orkio.realtime.rtb06")
    get_current_user = getattr(deps, "get_current_user", None) or _default_current_user
    get_db = getattr(deps, "get_db", None) or _default_db

    @router.post("/api/realtime/guard")
    def realtime_guard(
        body: RealtimeGuardReq,
        x_org_slug: Optional[str] = Header(default=None),
        user: Any = Depends(get_current_user),
        db: Any = Depends(get_db),
    ) -> Dict[str, Any]:
        org = _resolve_org_safe(deps, user, x_org_slug)
        guard_fn = getattr(deps, "_guard_realtime_message", None)
        blocked_reply = None

        if callable(guard_fn):
            try:
                blocked_reply = guard_fn(_safe_getattr(body, "message", ""))
            except Exception:
                blocked_reply = None

        return {
            "ok": True,
            "blocked": bool(blocked_reply),
            "reply": blocked_reply,
            "org": org,
            "rtb03": True,
        }

    @router.post("/api/realtime/client_secret")
    async def realtime_client_secret(
        body: RealtimeClientSecretReq,
        x_org_slug: Optional[str] = Header(default=None),
        user: Any = Depends(get_current_user),
        db: Any = Depends(get_db),
    ) -> JSONResponse:
        org = _resolve_org_safe(deps, user, x_org_slug)
        db_user = _lookup_db_user(deps, db, user, org)
        uid = str(_safe_getattr(user, "sub", None) or _safe_getattr(user, "id", "") or "").strip() or None

        mode = str(_safe_getattr(body, "mode", "") or "platform").strip().lower()
        response_profile = str(_safe_getattr(body, "response_profile", "") or "natural").strip().lower()
        language_profile = str(
            _safe_getattr(body, "language_profile", None)
            or _safe_getattr(body, "language", None)
            or "pt"
        ).strip().lower() or "pt"

        base_instructions = _build_instructions(
            deps,
            mode=mode,
            response_profile=response_profile,
            language_profile=language_profile,
        )

        thread_id = str(_safe_getattr(body, "thread_id", "") or "").strip()
        overlay, overlay_meta = _build_realtime_context_overlay(
            deps,
            db,
            org=org,
            user=user,
            db_user=db_user,
            thread_id=thread_id,
            uid=uid,
            logger=logger,
        )
        instructions = _append_instruction_overlay(base_instructions, overlay)

        secret = await _mint_client_secret(
            deps,
            body,
            instructions=instructions,
            resolved_language=language_profile,
            summit_runtime=(mode == "summit"),
            logger=logger,
        )

        return _json_response(
            {
                **_json_safe(secret),
                "org": org,
                "rtb03": True,
                "rtb06": True,
                "context": overlay_meta,
                "serialization_safe": "RTB03_RTB06",
            }
        )

    @router.post("/api/realtime/start")
    async def realtime_start(
        body: RealtimeStartReq,
        x_org_slug: Optional[str] = Header(default=None),
        user: Any = Depends(get_current_user),
        db: Any = Depends(get_db),
    ) -> JSONResponse:
        org = _resolve_org_safe(deps, user, x_org_slug)
        db_user = _lookup_db_user(deps, db, user, org)
        uid = str(_safe_getattr(user, "sub", None) or _safe_getattr(user, "id", "") or "").strip() or None
        is_admin = _is_admin_user(user, db_user)

        mode = str(_safe_getattr(body, "mode", "") or "platform").strip().lower()
        response_profile = str(_safe_getattr(body, "response_profile", "") or "natural").strip().lower()
        language_profile = str(
            _safe_getattr(body, "language_profile", None)
            or _safe_getattr(body, "language", None)
            or "pt"
        ).strip().lower() or "pt"

        ttl_requested = int(
            _safe_getattr(body, "ttl_seconds", None)
            or REALTIME_CLIENT_SECRET_TTL_SECONDS
        )
        effective_ttl = max(60, min(ttl_requested, REALTIME_CLIENT_SECRET_TTL_SECONDS))

        try:
            body.ttl_seconds = effective_ttl
        except Exception:
            pass

        thread_id = str(_safe_getattr(body, "thread_id", "") or "").strip() or _new_id("thread")
        agent_id = str(_safe_getattr(body, "agent_id", "") or "").strip() or None

        base_instructions = _build_instructions(
            deps,
            mode=mode,
            response_profile=response_profile,
            language_profile=language_profile,
        )

        overlay, overlay_meta = _build_realtime_context_overlay(
            deps,
            db,
            org=org,
            user=user,
            db_user=db_user,
            thread_id=thread_id,
            uid=uid,
            logger=logger,
        )
        instructions = _append_instruction_overlay(base_instructions, overlay)

        secret = await _mint_client_secret(
            deps,
            body,
            instructions=instructions,
            resolved_language=language_profile,
            summit_runtime=(mode == "summit"),
            logger=logger,
        )

        session_id = _new_id("rt")
        started_at = _now_ts()

        timebox = {
            "limited": False,
            "admin_bypass": bool(is_admin),
            "bypass": "admin" if is_admin else "no_hard_timebox",
            "max_seconds": None,
            "remaining_seconds": None,
            "cooldown_seconds": 0,
            "advisory_only": True,
            "recommended_seconds": REALTIME_ADVISORY_RECOMMENDED_SECONDS,
        }
        usage_advisory = _build_esg_usage_advisory()

        session_meta = {
            "patch": "RTB03_RTB06",
            "mode": mode,
            "response_profile": response_profile,
            "language_profile": language_profile,
            "context": overlay_meta,
        }

        _maybe_persist_realtime_session(
            deps,
            db,
            session_id=session_id,
            org=org,
            user_id=uid,
            thread_id=thread_id,
            started_at=started_at,
            mode=mode,
            agent_id=agent_id,
            meta=session_meta,
        )

        try:
            logger.warning(
                "RTB03_REALTIME_START_OK user_id=%s org=%s session_id=%s thread_id=%s "
                "admin=%s founder_identity=%s thread_context=%s messages=%s",
                uid,
                org,
                session_id,
                thread_id,
                bool(is_admin),
                bool(overlay_meta.get("founder_identity_injected")),
                bool(overlay_meta.get("thread_context_loaded")),
                overlay_meta.get("thread_context_messages"),
            )
        except Exception:
            pass

        safe_secret = _json_safe(secret)

        return _json_response(
            {
                "ok": True,
                "session_id": session_id,
                "thread_id": thread_id,
                "client_secret": safe_secret,
                "client_secret_value": safe_secret.get("value") if isinstance(safe_secret, dict) else None,
                "value": safe_secret.get("value") if isinstance(safe_secret, dict) else None,
                "timebox": _json_safe(timebox),
                "usage_advisory": _json_safe(usage_advisory),
                "started_at": started_at,
                "rtb03": True,
                "rtb06": True,
                "context": overlay_meta,
                "serialization_safe": "RTB03_RTB06",
                "timebox_policy": "advisory_only_esg",
            }
        )

    @router.post("/api/realtime/events:batch")
    def realtime_events_batch(
        body: RealtimeEventsBatchReq,
        x_org_slug: Optional[str] = Header(default=None),
        user: Any = Depends(get_current_user),
        db: Any = Depends(get_db),
    ) -> Dict[str, Any]:
        org = _resolve_org_safe(deps, user, x_org_slug)
        events = list(_safe_getattr(body, "events", []) or [])
        session_id = str(_safe_getattr(body, "session_id", "") or "").strip()
        uid = str(_safe_getattr(user, "sub", None) or _safe_getattr(user, "id", "") or "").strip() or None

        try:
            logger.warning(
                "RTB06_REALTIME_EVENTS_BATCH org=%s session_id=%s count=%s names=%s",
                org,
                session_id,
                len(events),
                ",".join([_event_name(ev) for ev in events[:20]]),
            )
        except Exception:
            pass

        promotion = _rtb06_promote_realtime_finals_to_messages(
            deps,
            db,
            org=org,
            user_id=uid,
            session_id=session_id,
            events=events,
            logger=logger,
        )

        return {
            "ok": True,
            "session_id": session_id,
            "received": len(events),
            "rtb03": True,
            "rtb06": True,
            "finals_promoted": promotion,
        }

    @router.get("/api/realtime/{session_id}")
    def realtime_get_session(
        session_id: str,
        finals_only: Optional[bool] = False,
        x_org_slug: Optional[str] = Header(default=None),
        user: Any = Depends(get_current_user),
        db: Any = Depends(get_db),
    ) -> JSONResponse:
        org = _resolve_org_safe(deps, user, x_org_slug)
        session_id_clean = str(session_id or "").strip()

        snapshot = None
        try:
            snapshot_fn = getattr(deps, "get_realtime_session_snapshot", None)
            if callable(snapshot_fn):
                snapshot = snapshot_fn(session_id_clean, org=org, db=db)
        except Exception:
            snapshot = None

        payload = {
            "ok": True,
            "session_id": session_id_clean,
            "org": org,
            "finals_only": bool(finals_only),
            "session": _json_safe(snapshot) if snapshot else None,
            "finals": {
                "user_text": "",
                "assistant_text": "",
                "turns": [],
            },
            "rtb03": True,
            "serialization_safe": "RTB03_RTB06",
            "compatibility_endpoint": "GET /api/realtime/{session_id}",
        }

        try:
            logger.warning(
                "RTB03_REALTIME_GET_SESSION_COMPAT org=%s session_id=%s finals_only=%s has_snapshot=%s",
                org,
                session_id_clean,
                bool(finals_only),
                bool(snapshot),
            )
        except Exception:
            pass

        return _json_response(payload)

    @router.post("/api/realtime/end")
    def realtime_end(
        body: RealtimeEndReq,
        x_org_slug: Optional[str] = Header(default=None),
        user: Any = Depends(get_current_user),
        db: Any = Depends(get_db),
    ) -> Dict[str, Any]:
        org = _resolve_org_safe(deps, user, x_org_slug)
        session_id = str(_safe_getattr(body, "session_id", "") or "").strip() or None
        reason = str(_safe_getattr(body, "reason", "") or "client_end").strip() or "client_end"
        ended_at = _now_ts()

        persisted = _maybe_mark_realtime_session_ended(
            deps,
            db,
            session_id=session_id,
            ended_at=ended_at,
            reason=reason,
        )

        try:
            logger.warning(
                "RTB03_REALTIME_END org=%s session_id=%s reason=%s persisted=%s",
                org,
                session_id,
                reason,
                bool(persisted),
            )
        except Exception:
            pass

        return {
            "ok": True,
            "session_id": session_id,
            "ended_at": ended_at,
            "persisted": bool(persisted),
            "rtb03": True,
        }

    return router


__all__ = ["build_realtime_router"]
