# PATCH_33_REV_B_REALTIME_PROVIDER_PAYLOAD_SANITIZER
# ORKIO_RTB06_REALTIME_FINALS_MESSAGES_BRIDGE
# Backend-only PATCH_MINIMUM for routes/realtime.py
# PATCH_30_SERVER_SPEAKER_AUTHORITY_CLIENT_ECHO_QUARANTINE
# PATCH_32_MANUAL_AGENT_AUTHORITY_MODE
# PATCH_32_PREDEPLOY_PREMIUM_MANUAL_AGENT_AUTHORITY_AUDIT
# PATCH_32_REV_C_PROFILE_ADDRESS_MERGE
# PATCH_32_REV_D_TEAM_PANEL_PRESTAGING
# PATCH_32_REV_E_MANUAL_BUTTON_STICKY_STATE
# PATCH_32_REV_F_MANUAL_BUTTON_LOCK_PERSISTENCE
# PATCH_32_REV_G_MANUAL_LOCK_CONTRACT_PROPAGATION
# PATCH_32_REV_H_MANUAL_LOCK_STAGING_PROOF
# PATCH_32_REV_I_MANUAL_LOCK_STAGING_PROOF_SILENCE
# PATCH_32_REV_J_MANUAL_LOCK_STAGING_PROOF_PRODUCTION_GUARD
# PATCH_33_TEAM_CONVERSATION_ORCHESTRATOR
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
import re
import time
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

try:
    from app.runtime.agent_registry import (
        AGENT_REGISTRY_VERSION,
        agent_display_name as registry_agent_display_name,
        canonical_agent_slug as registry_canonical_agent_slug,
        realtime_role_line as registry_realtime_role_line,
    )
except Exception:  # pragma: no cover
    AGENT_REGISTRY_VERSION = "PATCH_23_CANONICAL_AGENT_REGISTRY_V1"
    registry_agent_display_name = None  # type: ignore
    registry_canonical_agent_slug = None  # type: ignore
    registry_realtime_role_line = None  # type: ignore


try:
    from app.runtime.profile_preferences import (  # type: ignore
        PROFILE_ADDRESS_PREFERENCE_VERSION,
        build_profile_address_preference_context,
        resolve_profile_address_names,
    )
except Exception:  # pragma: no cover
    PROFILE_ADDRESS_PREFERENCE_VERSION = "PROFILE_ADDRESS_PREFERENCE_V1"

    def build_profile_address_preference_context(*args: Any, **kwargs: Any) -> str:
        return ""

    def resolve_profile_address_names(*args: Any, **kwargs: Any) -> List[str]:
        return []


from fastapi import APIRouter, Depends, Header, HTTPException, Request
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
        agent_ids: Optional[Any] = None
        thread_id: Optional[str] = None
        dest_mode: Optional[str] = None
        visible_agent: Optional[str] = None
        target_agent_slug: Optional[str] = None
        manual_target_slug: Optional[str] = None
        requested_agent_names: Optional[Any] = None
        target_agent_slugs: Optional[Any] = None
        multi_agent_turn: Optional[bool] = None
        response_control: Optional[str] = None
        manual_agent_lock: Optional[bool] = None
        manual_agent_source: Optional[str] = None
        manual_authority_version: Optional[str] = None
        manual_sticky_state_version: Optional[str] = None
        manual_lock_persistence_version: Optional[str] = None
        manual_lock_staging_proof_version: Optional[str] = None
        manual_lock_staging_proof_production_guard_version: Optional[str] = None
        auto_handoff_enabled: Optional[bool] = None
        manual_team_panel_required: Optional[bool] = None
        manual_team_panel_order: Optional[Any] = None
        team_panel_version: Optional[str] = None
        team_panel_mode: Optional[str] = None
        team_panel_voice_moderator_slug: Optional[str] = None
        manual_team_conversation_active: Optional[bool] = None
        manual_team_focus_slug: Optional[str] = None
        manual_team_turn_queue: Optional[Any] = None
        manual_team_turn_index: Optional[int] = None
        team_conversation_mode: Optional[str] = None
        team_conversation_orchestrator_version: Optional[str] = None
        team_conversation_staging_verification_version: Optional[str] = None
        realtime_provider_payload_sanitizer_version: Optional[str] = None
        live_agent_switch_runtime_fix_version: Optional[str] = None
        client_controlled_response: Optional[bool] = None
        preferred_address_names: Optional[Any] = None
        profile_address_preference_version: Optional[str] = None

    class RealtimeStartReq(BaseModel):
        agent_id: Optional[str] = None
        agent_ids: Optional[Any] = None
        thread_id: Optional[str] = None
        voice: Optional[str] = None
        model: Optional[str] = None
        ttl_seconds: Optional[int] = 120
        mode: Optional[str] = None
        response_profile: Optional[str] = None
        language_profile: Optional[str] = None
        language: Optional[str] = None
        dest_mode: Optional[str] = None
        visible_agent: Optional[str] = None
        target_agent_slug: Optional[str] = None
        manual_target_slug: Optional[str] = None
        requested_agent_names: Optional[Any] = None
        target_agent_slugs: Optional[Any] = None
        multi_agent_turn: Optional[bool] = None
        response_control: Optional[str] = None
        manual_agent_lock: Optional[bool] = None
        manual_agent_source: Optional[str] = None
        manual_authority_version: Optional[str] = None
        manual_sticky_state_version: Optional[str] = None
        manual_lock_persistence_version: Optional[str] = None
        manual_lock_staging_proof_version: Optional[str] = None
        manual_lock_staging_proof_production_guard_version: Optional[str] = None
        auto_handoff_enabled: Optional[bool] = None
        manual_team_panel_required: Optional[bool] = None
        manual_team_panel_order: Optional[Any] = None
        team_panel_version: Optional[str] = None
        team_panel_mode: Optional[str] = None
        team_panel_voice_moderator_slug: Optional[str] = None
        manual_team_conversation_active: Optional[bool] = None
        manual_team_focus_slug: Optional[str] = None
        manual_team_turn_queue: Optional[Any] = None
        manual_team_turn_index: Optional[int] = None
        team_conversation_mode: Optional[str] = None
        team_conversation_orchestrator_version: Optional[str] = None
        team_conversation_staging_verification_version: Optional[str] = None
        realtime_provider_payload_sanitizer_version: Optional[str] = None
        live_agent_switch_runtime_fix_version: Optional[str] = None
        client_controlled_response: Optional[bool] = None
        preferred_address_names: Optional[Any] = None
        profile_address_preference_version: Optional[str] = None

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
    from app.runtime.realtime_meeting_orchestrator import (  # type: ignore
        build_meeting_directive,
        summarize_directive_for_log,
    )
except Exception:  # pragma: no cover
    def build_meeting_directive(*args: Any, **kwargs: Any) -> Optional[Dict[str, Any]]:
        return None

    def summarize_directive_for_log(directive: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {"status": "unavailable" if directive is None else "unknown"}


try:
    from app.runtime.meeting_state import (  # type: ignore
        MEETING_STATE_VERSION,
        apply_turn_to_meeting_state,
        build_initial_meeting_state,
        meeting_state_from_meta,
        merge_meeting_state_into_meta,
        summarize_meeting_state_for_log,
        update_meeting_state_from_directive,
    )
except Exception:  # pragma: no cover
    MEETING_STATE_VERSION = "PATCH_25_MEETING_STATE_V1"

    def build_initial_meeting_state(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {}

    def apply_turn_to_meeting_state(state: Optional[Dict[str, Any]], *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return state if isinstance(state, dict) else {}

    def update_meeting_state_from_directive(state: Optional[Dict[str, Any]], *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return state if isinstance(state, dict) else {}

    def meeting_state_from_meta(meta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return (meta or {}).get("meeting_state", {}) if isinstance(meta, dict) else {}

    def merge_meeting_state_into_meta(meta: Optional[Dict[str, Any]], state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        out = dict(meta or {})
        if isinstance(state, dict) and state:
            out["meeting_state"] = state
        return out

    def summarize_meeting_state_for_log(state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {"version": MEETING_STATE_VERSION}


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



try:
    from app.runtime.meeting_observability import (  # type: ignore
        MEETING_OBSERVABILITY_VERSION,
        build_meeting_transition_log,
        summarize_transition_for_response,
        transition_log_line,
    )
except Exception:  # pragma: no cover
    MEETING_OBSERVABILITY_VERSION = "PATCH_29_MEETING_OBSERVABILITY_V1"

    def build_meeting_transition_log(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        return {
            "event": "meeting_transition",
            "observability_version": MEETING_OBSERVABILITY_VERSION,
            "transition_reason": "observability_unavailable",
        }

    def summarize_transition_for_response(event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return event if isinstance(event, dict) else {}

    def transition_log_line(event: Optional[Dict[str, Any]]) -> str:
        try:
            return json.dumps(event or {}, ensure_ascii=False, sort_keys=True)
        except Exception:
            return "{}"

class RealtimeEventsBatchReq(BaseModel):
    session_id: str
    events: List[RealtimeEventIn] = []
    # PATCH_22_DIRECT_AGENT_ADDRESSING:
    # Optional client-side routing hints captured after the frontend applies a
    # direct agent address such as "Orion, ...". These are advisory and fail-open.
    agent_id: Optional[str] = None
    dest_mode: Optional[str] = None
    visible_agent: Optional[str] = None
    target_agent_slug: Optional[str] = None
    manual_target_slug: Optional[str] = None
    requested_agent_names: Optional[Any] = None
    # PATCH_25_MEETING_STATE_PERSISTENTE:
    # Frontend may echo the latest room state so backend can merge it into
    # RealtimeSession.meta without a migration.
    meeting_state: Optional[Dict[str, Any]] = None
    # PATCH_27_MULTI_AGENT_RESPONSE_CONTROL:
    # Advisory route metadata for sequenced team turns. Optional/fail-open.
    target_agent_slugs: Optional[List[str]] = None
    multi_agent_turn: Optional[bool] = None
    response_control: Optional[str] = None
    # PATCH_32_MANUAL_AGENT_AUTHORITY_MODE:
    # Optional/fail-open manual button contract from the App Console. When present,
    # it tells realtime events:batch that the selected UI button is the authority
    # and natural-language handoff should not override the active speaker.
    manual_agent_lock: Optional[bool] = None
    manual_agent_source: Optional[str] = None
    manual_authority_version: Optional[str] = None
    manual_sticky_state_version: Optional[str] = None
    manual_lock_persistence_version: Optional[str] = None
    manual_lock_staging_proof_version: Optional[str] = None
    manual_lock_staging_proof_production_guard_version: Optional[str] = None
    auto_handoff_enabled: Optional[bool] = None
    # PATCH_32_REV_D_TEAM_PANEL_PRESTAGING:
    # Optional/fail-open Team panel contract. When manual_target_slug=team, these
    # fields prevent Team from being treated as a single specialist by older
    # dispatchers/HF constraints.
    manual_team_panel_required: Optional[bool] = None
    manual_team_panel_order: Optional[List[str]] = None
    team_panel_version: Optional[str] = None
    team_panel_mode: Optional[str] = None
    team_panel_voice_moderator_slug: Optional[str] = None
    # PATCH_33_TEAM_CONVERSATION_ORCHESTRATOR:
    # Optional/fail-open Team room contract.
    manual_team_conversation_active: Optional[bool] = None
    manual_team_focus_slug: Optional[str] = None
    manual_team_turn_queue: Optional[List[str]] = None
    manual_team_turn_index: Optional[int] = None
    team_conversation_mode: Optional[str] = None
    team_conversation_orchestrator_version: Optional[str] = None
    team_conversation_staging_verification_version: Optional[str] = None


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


async def _request_json_field(request: Optional[Request], name: str, default: Any = None) -> Any:
    if request is None:
        return default
    try:
        payload = await request.json()
        if isinstance(payload, dict):
            return payload.get(name, default)
    except Exception:
        return default
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
    profile_address_names: Any = None,
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

    try:
        profile_address_context = build_profile_address_preference_context(
            user=user,
            db_user=db_user,
            explicit=profile_address_names,
        )
        if profile_address_context:
            overlay_parts.append(profile_address_context)
            meta["profile_address_preference_injected"] = True
            meta["profile_address_preference_version"] = PROFILE_ADDRESS_PREFERENCE_VERSION
            meta["profile_address_names_count"] = len(resolve_profile_address_names(
                user=user,
                db_user=db_user,
                explicit=profile_address_names,
            ))
    except Exception as exc:
        meta["profile_address_preference_error"] = str(exc)[:120]

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
    create_response: bool = True,
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
                        "create_response": bool(create_response),
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
    create_response: bool = True,
) -> Dict[str, Any]:
    if _payload_looks_ga_compatible(payload):
        # Ensure patched instructions and turn policy are not dropped by a stale builder.
        try:
            session = payload.get("session")
            if isinstance(session, dict) and instructions:
                session["instructions"] = instructions
            audio = session.get("audio") if isinstance(session, dict) else None
            audio_input = audio.get("input") if isinstance(audio, dict) else None
            turn_detection = audio_input.get("turn_detection") if isinstance(audio_input, dict) else None
            if isinstance(turn_detection, dict):
                turn_detection["create_response"] = bool(create_response)
        except Exception:
            pass
        return payload

    return _build_basic_realtime_payload(
        model=model,
        voice=voice,
        ttl_seconds=ttl_seconds,
        instructions=instructions,
        resolved_language=resolved_language,
        create_response=create_response,
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


def _coerce_realtime_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        items = value
    elif isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                items = parsed
            else:
                items = [raw]
        except Exception:
            items = re.split(r"[;,|]", raw)
    else:
        items = [value]

    out: List[str] = []
    for item in items:
        text = str(item or "").strip()
        if text and text not in out:
            out.append(text)
    return out


def _normalize_realtime_agent_slug(value: Any, *, default: str = "") -> str:
    # PATCH_23_AGENT_REGISTRY_CANONICO:
    # Realtime slug resolution now delegates to the canonical backend registry.
    try:
        if callable(registry_canonical_agent_slug):
            resolved = registry_canonical_agent_slug(value, default="", allow_unknown=False)
            if resolved:
                return str(resolved)
    except Exception:
        pass

    raw = str(value or "").strip().lower()
    if not raw:
        return default

    simplified = (
        raw
        .replace("@", " ")
        .replace("ó", "o")
        .replace("ò", "o")
        .replace("õ", "o")
        .replace("ô", "o")
        .replace("á", "a")
        .replace("à", "a")
        .replace("ã", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ú", "u")
        .replace("ç", "c")
    )
    compact = re.sub(r"[^a-z0-9]+", " ", simplified).strip()

    # Defensive fallback retained for bootstraps where registry import is unavailable.
    if any(token in compact for token in ("orion", "oria", "auria", "aurya", "arian", "aryan", "orlan", "warren")):
        return "orion"
    if "cto" in compact or "tecnico" in compact or "technical" in compact:
        return "orion"
    if any(token in compact for token in ("chris", "cris", "cfo", "financeiro", "financial")):
        return "chris"
    if "laura" in compact or "business plan" in compact or "pitch" in compact:
        return "laura"
    if "auditor" in compact or "auditoria" in compact or "ao 01" in compact or "ao01" in compact:
        return "auditor"
    if any(token in compact for token in ("team", "time", "equipe", "squad", "war room", "warroom")):
        return "team"
    if any(token in compact for token in ("orkio", "ork", "patroai")):
        return "orkio"

    return default


def _agent_display_name_from_slug(slug: str) -> str:
    try:
        if callable(registry_agent_display_name):
            return str(registry_agent_display_name(slug, default="Orkio") or "Orkio")
    except Exception:
        pass
    return {
        "orion": "Orion",
        "chris": "Chris",
        "laura": "Laura",
        "auditor": "Auditor",
        "team": "Team",
        "orkio": "Orkio",
    }.get(str(slug or "").strip().lower(), "Orkio")




def _coerce_manual_team_panel_order(value: Any = None) -> List[str]:
    """PATCH_32_REV_D: deterministic Team panel order.

    Fail-open and canonical. It must include Laura/Chris/Orion even if a stale
    client/API payload only sends ["orkio"] or omits the list.
    """
    raw_items: List[Any] = []
    if isinstance(value, str):
        raw = value.strip()
        if raw:
            try:
                parsed = json.loads(raw)
                raw_items = parsed if isinstance(parsed, list) else [raw]
            except Exception:
                raw_items = re.split(r"[;,|]", raw)
    elif isinstance(value, (list, tuple, set)):
        raw_items = list(value)
    elif value:
        raw_items = [value]

    out: List[str] = []
    for item in raw_items:
        slug = _normalize_realtime_agent_slug(item, default="")
        if slug in PATCH_32_REV_D_TEAM_PANEL_ORDER and slug not in out:
            out.append(slug)

    # Add any missing canonical Team members in deterministic order.
    for slug in PATCH_32_REV_D_TEAM_PANEL_ORDER:
        if slug not in out:
            out.append(slug)

    return out


def _manual_team_panel_names(slugs: Optional[List[str]] = None) -> List[str]:
    return [_agent_display_name_from_slug(slug) for slug in (slugs or PATCH_32_REV_D_TEAM_PANEL_ORDER)]

def _patch33_is_team_conversation_active(*values: Any) -> bool:
    for value in values:
        if isinstance(value, bool) and value:
            return True
        raw = str(value or "").strip()
        if not raw:
            continue
        low = raw.lower()
        if low in {"1", "true", "yes", "on"}:
            return True
        if raw in {
            PATCH_33_TEAM_CONVERSATION_ORCHESTRATOR_VERSION,
            PATCH_33_TEAM_CONVERSATION_RESPONSE_CONTROL,
            PATCH_33_TEAM_CONVERSATION_MODE,
        }:
            return True
    return False


def _patch33_team_focus_slug(value: Any = None, default: str = "orkio") -> str:
    slug = _normalize_realtime_agent_slug(value, default="")
    if slug and slug != "team":
        return slug
    return default


def _patch33_team_turn_queue(value: Any = None, focus_slug: str = "orkio") -> List[str]:
    base = _coerce_manual_team_panel_order(value)
    focus = _patch33_team_focus_slug(focus_slug, default="")
    if focus and focus in PATCH_32_REV_D_TEAM_PANEL_ORDER:
        return [focus] + [slug for slug in base if slug != focus]
    return base


def _find_agent_row_by_hint(deps: SimpleNamespace, db: Any, org: str, hint: str) -> Any:
    Agent = getattr(deps, "Agent", None)
    if db is None or Agent is None or select is None or not hint:
        return None

    raw = str(hint or "").strip()
    slug = _normalize_realtime_agent_slug(raw, default="")
    candidates = [raw]
    if slug:
        candidates.extend([slug, _agent_display_name_from_slug(slug)])

    seen: List[str] = []
    for item in candidates:
        item = str(item or "").strip()
        if item and item not in seen:
            seen.append(item)

    for candidate in seen:
        try:
            row = db.execute(
                select(Agent).where(
                    Agent.org_slug == org,
                    Agent.id == candidate,
                ).limit(1)
            ).scalar_one_or_none()
            if row:
                return row
        except Exception:
            pass

    for candidate in seen:
        try:
            row = db.execute(
                select(Agent).where(
                    Agent.org_slug == org,
                    Agent.name.ilike(candidate),
                ).limit(1)
            ).scalar_one_or_none()
            if row:
                return row
        except Exception:
            pass

    return None


def _agent_row_slug(row: Any, fallback: str = "") -> str:
    if not row:
        return fallback
    for key in ("slug", "agent_slug", "code", "key", "name", "id"):
        slug = _normalize_realtime_agent_slug(_safe_getattr(row, key, ""), default="")
        if slug:
            return slug
    return fallback


def _resolve_realtime_agent_context(
    deps: SimpleNamespace,
    db: Any,
    *,
    org: str,
    body: Any,
    explicit_agent_id: Optional[str],
) -> Dict[str, Any]:
    dest_mode = str(_safe_getattr(body, "dest_mode", "") or "").strip().lower()
    visible_agent = str(_safe_getattr(body, "visible_agent", "") or "").strip()
    manual_target_slug = str(_safe_getattr(body, "manual_target_slug", "") or "").strip()
    target_agent_slug = str(_safe_getattr(body, "target_agent_slug", "") or "").strip()
    requested_names = _coerce_realtime_list(_safe_getattr(body, "requested_agent_names", None))
    agent_ids = _coerce_realtime_list(_safe_getattr(body, "agent_ids", None))

    hints: List[str] = []
    for item in (manual_target_slug, target_agent_slug, visible_agent, explicit_agent_id):
        if item:
            hints.append(str(item))
    hints.extend(agent_ids)
    hints.extend(requested_names)

    slug = ""
    row = None
    for hint in hints:
        slug = _normalize_realtime_agent_slug(hint, default="")
        row = _find_agent_row_by_hint(deps, db, org, hint)
        if row:
            slug = _agent_row_slug(row, fallback=slug)
        if slug:
            break

    if not slug:
        if dest_mode == "team":
            slug = "team"
        else:
            slug = "orkio"

    display_name = _agent_display_name_from_slug(slug)
    row_id = str(_safe_getattr(row, "id", "") or "").strip() if row else ""
    row_name = str(_safe_getattr(row, "name", "") or "").strip() if row else ""

    return {
        "slug": slug,
        "display_name": display_name,
        "agent_id": row_id or (explicit_agent_id if slug != "team" else None),
        "agent_name": row_name or display_name,
        "dest_mode": dest_mode or ("team" if slug == "team" else "single"),
        "visible_agent": visible_agent or display_name,
        "target_agent_slug": target_agent_slug or slug,
        "requested_agent_names": requested_names,
        "agent_ids": agent_ids,
    }


def _build_realtime_agent_identity_block(agent_context: Optional[Dict[str, Any]] = None) -> str:
    ctx = agent_context if isinstance(agent_context, dict) else {}
    slug = str(ctx.get("slug") or "orkio").strip().lower()
    name = _agent_display_name_from_slug(slug)

    try:
        role_line = (
            registry_realtime_role_line(slug)
            if callable(registry_realtime_role_line)
            else ""
        )
    except Exception:
        role_line = ""
    if not role_line:
        role_line = {
            "orion": "Você é Orion, agente interno CTO técnico da Patroai, responsável por diagnóstico técnico, arquitetura, bugs, logs, deploy, realtime e orquestração.",
            "chris": "Você é Chris, agente interno financeiro/estratégico da Patroai, responsável por análise financeira, precificação, viabilidade, riscos comerciais e estratégia de receita.",
            "laura": "Você é Laura, agente interno de narrativa, business plan e investidores da Patroai.",
            "auditor": "Você é Auditor, agente/função de auditoria externa, responsável por revisão crítica, evidências e riscos.",
            "team": "Você está no modo Team, atuando como coordenador de sala executiva multiagente da Patroai.",
            "orkio": "Você é Orkio, agente executivo principal da plataforma Patroai.",
        }.get(slug, "Você é Orkio, agente executivo principal da plataforma Patroai.")

    if slug == "team":
        direct_identity = (
            "- Se o usuário perguntar quem está falando, diga que é o modo Team coordenando a conversa, e identifique o agente que assumirá cada resposta quando houver handoff.\n"
            "- Não finja que vários agentes falaram se não houve troca técnica de speaker ou resposta registrada.\n"
            "- Para acionar Orion/Chris, sinalize o handoff de forma clara e responda como o agente correto apenas quando a sessão estiver instruída para isso."
        )
    else:
        direct_identity = (
            f"- Se o usuário perguntar quem está falando, responda: 'Eu sou {name}.'.\n"
            f"- O speaker visual, a resposta e a persistência devem ser coerentes com {name}.\n"
            f"- Não diga que você é Orkio quando a identidade ativa for {name}, exceto para explicar que Orkio é a plataforma/agente coordenador."
        )

    return (
        "EFATA777 V7 — IDENTIDADE ATIVA, TURNO CONTROLADO E VERDADE OPERACIONAL DO REALTIME\n"
        f"{role_line}\n"
        f"- Identidade ativa: {name}.\n"
        f"- Slug ativo: {slug}.\n"
        f"- Agent Registry: {AGENT_REGISTRY_VERSION}.\n"
        f"{direct_identity}\n"
        "- Não afirme que executou auditoria, abriu War Room, acionou agentes, enviou push, fez deploy, commit, PR ou integração se a ação não estiver tecnicamente confirmada por ferramenta, endpoint ou log.\n"
        "- Quando algo for apenas proposta, intenção ou plano, diga explicitamente que é proposta/intenção/plano.\n"
        "- Para Daniel admin/founder, mantenha tom executivo, objetivo, técnico e honesto."
    )


def _build_instructions(
    deps: SimpleNamespace,
    *,
    mode: str,
    response_profile: str,
    language_profile: str,
    agent_context: Optional[Dict[str, Any]] = None,
) -> str:
    builder = getattr(deps, "build_summit_instructions", None)
    sensitive_guard = getattr(deps, "_sensitive_guard_instruction", None)

    identity_block = _build_realtime_agent_identity_block(agent_context)
    instructions = ""

    if callable(builder):
        try:
            instructions = str(
                builder(
                    mode=mode,
                    agent_instructions=identity_block,
                    language_profile=language_profile,
                    response_profile=response_profile,
                )
                or ""
            ).strip()
        except Exception:
            instructions = ""

    if not instructions:
        instructions = (
            identity_block
            + "\n\nResponda sempre em português do Brasil, com clareza, objetividade, segurança operacional e sem inventar evidência."
        )
    elif identity_block not in instructions:
        # If the summit builder returns a generic Orkio prompt, the active agent
        # identity overlay must still win for Realtime.
        instructions = f"{instructions}\n\n{identity_block}"

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
    client_controlled_response = bool(_safe_getattr(body, "client_controlled_response", False))
    create_response = not client_controlled_response

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
                create_response=create_response,
            )
    else:
        payload = _build_basic_realtime_payload(
            model=model,
            voice=voice,
            ttl_seconds=ttl_seconds,
            instructions=instructions,
            resolved_language=resolved_language,
            create_response=create_response,
        )

    payload = _normalize_realtime_payload_for_ga(
        payload,
        model=model,
        voice=voice,
        ttl_seconds=ttl_seconds,
        instructions=instructions,
        resolved_language=resolved_language,
        create_response=create_response,
    )

    payload, patch33_revb_removed_keys = _patch33_revb_sanitize_provider_payload(payload)
    try:
        logger.warning(
            "PATCH33_REV_B_REALTIME_PROVIDER_PAYLOAD_SANITIZER version=%s provider_session_payload_clean=%s removed_count=%s removed_keys=%s",
            PATCH_33_REV_B_REALTIME_PROVIDER_PAYLOAD_SANITIZER_VERSION,
            True,
            len(patch33_revb_removed_keys),
            json.dumps(patch33_revb_removed_keys, ensure_ascii=False),
        )
    except Exception:
        pass

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
            # PATCH_27_AO01_PATCH26_FIX:
            # Preserve meta as a Python mapping on initial session creation.
            # PATCH 26 already preserved type on update; this closes the remaining
            # JSON/JSONB risk reported by AO-01. TEXT-only deployments can still
            # serialize through the ORM/db layer if configured that way.
            values["meta"] = meta

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
        "agent_slug": None,
        "dest_mode": None,
        "meta": {},
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

        meta_raw = _safe_getattr(rs, "meta", None)
        meta_obj: Dict[str, Any] = {}
        if isinstance(meta_raw, dict):
            meta_obj = meta_raw
        elif isinstance(meta_raw, str) and meta_raw.strip():
            try:
                parsed_meta = json.loads(meta_raw)
                if isinstance(parsed_meta, dict):
                    meta_obj = parsed_meta
            except Exception:
                meta_obj = {}
        context["meta"] = meta_obj
        context["meeting_state"] = meeting_state_from_meta(meta_obj)

        agent_meta = meta_obj.get("agent") if isinstance(meta_obj.get("agent"), dict) else {}
        agent_slug = _normalize_realtime_agent_slug(
            agent_meta.get("slug")
            or agent_meta.get("agent_slug")
            or agent_meta.get("display_name")
            or agent_meta.get("name")
            or agent_meta.get("agent_id")
            or context.get("agent_id")
            or "",
            default="",
        )
        if agent_slug:
            context["agent_slug"] = agent_slug
        meeting_state = context.get("meeting_state") if isinstance(context.get("meeting_state"), dict) else {}
        meeting_active_slug = str(meeting_state.get("active_speaker_slug") or "").strip()
        if meeting_active_slug:
            context["meeting_active_speaker_slug"] = meeting_active_slug
            context["meeting_active_speaker_name"] = str(meeting_state.get("active_speaker_name") or "").strip()
        dest_mode = str(meta_obj.get("dest_mode") or agent_meta.get("dest_mode") or meeting_state.get("mode") or "").strip().lower()
        if dest_mode:
            context["dest_mode"] = dest_mode
    except Exception:
        return context

    return context


def _maybe_update_realtime_session_meeting_state(
    deps: SimpleNamespace,
    db: Any,
    *,
    session_id: str,
    meeting_state: Optional[Dict[str, Any]],
    logger: Optional[logging.Logger] = None,
) -> bool:
    """Persist PATCH_25 meeting state in RealtimeSession.meta without migrations."""
    if not session_id or not isinstance(meeting_state, dict) or not meeting_state:
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

        meta_raw = _safe_getattr(rs, "meta", None)
        meta_obj: Dict[str, Any] = {}
        if isinstance(meta_raw, dict):
            meta_obj = dict(meta_raw)
        elif isinstance(meta_raw, str) and meta_raw.strip():
            try:
                parsed_meta = json.loads(meta_raw)
                if isinstance(parsed_meta, dict):
                    meta_obj = parsed_meta
            except Exception:
                meta_obj = {}

        next_meta = merge_meeting_state_into_meta(meta_obj, meeting_state)
        try:
            # PATCH_26_AO01_PATCH25_FIX:
            # Preserve the runtime type of RealtimeSession.meta. Some deployments
            # store meta as TEXT (string JSON), while others use JSON/JSONB and
            # expect a Python dict. Do not stringify dict-backed columns.
            if isinstance(meta_raw, str):
                setattr(rs, "meta", json.dumps(next_meta, ensure_ascii=False))
            else:
                setattr(rs, "meta", next_meta)
        except Exception:
            return False

        db.add(rs)
        db.commit()
        return True
    except Exception as err:
        try:
            db.rollback()
        except Exception:
            pass
        try:
            if logger:
                logger.warning("PATCH25_MEETING_STATE_PERSIST_FAILED session_id=%s err=%s", session_id, err)
        except Exception:
            pass
        return False


def _merge_client_meeting_state(
    server_state: Optional[Dict[str, Any]],
    client_state: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Client echo is advisory; server keys win when present."""
    if not isinstance(client_state, dict):
        return server_state if isinstance(server_state, dict) else {}
    if not isinstance(server_state, dict) or not server_state:
        return client_state
    merged = dict(client_state)
    merged.update(server_state)
    if server_state.get("participant_slugs"):
        merged["participant_slugs"] = server_state.get("participant_slugs")
    if server_state.get("participants"):
        merged["participants"] = server_state.get("participants")
    return merged


PATCH_30_SERVER_SPEAKER_AUTHORITY_VERSION = (
    "PATCH_30_SERVER_SPEAKER_AUTHORITY_CLIENT_ECHO_QUARANTINE_V1"
)

PATCH_32_MANUAL_AGENT_AUTHORITY_VERSION = "PATCH_32_MANUAL_AGENT_AUTHORITY_MODE_V1"
PATCH_32_REV_C_MANUAL_TARGET_SOURCE_OF_TRUTH_VERSION = "PATCH_32_REV_C_MANUAL_TARGET_SOURCE_OF_TRUTH_V1"
PATCH_32_PREDEPLOY_PREMIUM_VERSION = "PATCH_32_PREDEPLOY_MANUAL_AGENT_AUTHORITY_VOICE_SYNC_V1"
PATCH_32_REV_D_TEAM_PANEL_VERSION = "PATCH_32_REV_D_TEAM_PANEL_PRESTAGING_V1"
PATCH_32_REV_D_TEAM_PANEL_ORDER = ["orkio", "orion", "chris", "laura"]
PATCH_32_REV_D_TEAM_PANEL_MODE = "manual_team_panel_deterministic_queue"
PATCH_32_REV_D_TEAM_PANEL_VOICE_MODERATOR_SLUG = "orkio"
PATCH_32_REV_E_MANUAL_BUTTON_STICKY_STATE_VERSION = "PATCH_32_REV_E_MANUAL_BUTTON_STICKY_STATE_V1"
PATCH_32_REV_F_MANUAL_BUTTON_LOCK_PERSISTENCE_VERSION = "PATCH_32_REV_F_MANUAL_BUTTON_LOCK_PERSISTENCE_V1"
PATCH_32_REV_H_MANUAL_LOCK_STAGING_PROOF_VERSION = "PATCH_32_REV_H_MANUAL_LOCK_STAGING_PROOF_V1"
PATCH_32_REV_J_MANUAL_LOCK_STAGING_PROOF_PRODUCTION_GUARD_VERSION = "PATCH_32_REV_J_MANUAL_LOCK_STAGING_PROOF_PRODUCTION_GUARD_V1"
PATCH_33_TEAM_CONVERSATION_ORCHESTRATOR_VERSION = "PATCH_33_TEAM_CONVERSATION_ORCHESTRATOR_V1"
PATCH_33_REV_A_TEAM_CONVERSATION_STAGING_VERIFICATION_VERSION = "PATCH_33_REV_A_TEAM_CONVERSATION_STAGING_VERIFICATION_V1"
PATCH_33_REV_B_REALTIME_PROVIDER_PAYLOAD_SANITIZER_VERSION = "PATCH_33_REV_B_REALTIME_PROVIDER_PAYLOAD_SANITIZER_V1"
PATCH_33_REV_C_LIVE_AGENT_SWITCH_RUNTIME_FIX_VERSION = "PATCH_33_REV_C_LIVE_AGENT_SWITCH_RUNTIME_FIX_V1"
PATCH_33_TEAM_CONVERSATION_RESPONSE_CONTROL = "team_conversation_orchestrator"
PATCH_33_TEAM_CONVERSATION_MODE = "team_conversation_room"



PATCH_33_REV_B_PROVIDER_INTERNAL_SESSION_KEYS = {
    "agent_id",
    "agent_ids",
    "visible_agent",
    "target_agent_slug",
    "target_agent_slugs",
    "requested_agent_names",
    "multi_agent_turn",
    "response_control",
    "dest_mode",
    "manual_agent_lock",
    "manual_agent_source",
    "manual_authority_source",
    "manual_authority_updated_at",
    "manual_authority_version",
    "manual_target_slug",
    "manual_sticky_state_version",
    "manual_lock_persistence_version",
    "manual_lock_staging_proof_version",
    "manual_lock_staging_proof_production_guard_version",
    "manual_lock_contract_propagation_version",
    "manual_team_panel_required",
    "manual_team_panel_order",
    "manual_team_conversation_active",
    "manual_team_focus_slug",
    "manual_team_turn_queue",
    "manual_team_turn_index",
    "team_panel_version",
    "team_panel_mode",
    "team_panel_voice_moderator_slug",
    "team_conversation_mode",
    "team_conversation_orchestrator_version",
    "team_conversation_staging_verification_version",
    "session_voice_sync_version",
    "profile_address_preference_version",
    "preferred_address_names",
    "auto_handoff_enabled",
    "auto_handoff_ignored",
    "realtime_voice_agent_slug",
    "realtime_provider_payload_sanitizer_version",
    "live_agent_switch_runtime_fix_version",
}


def _patch33_revb_is_internal_provider_session_key(key: Any) -> bool:
    safe_key = str(key or "").strip()
    if not safe_key:
        return False
    return (
        safe_key.startswith("manual_")
        or safe_key.startswith("team_")
        or safe_key.startswith("target_agent")
        or safe_key.startswith("requested_agent")
        or safe_key.startswith("profile_address")
        or safe_key in PATCH_33_REV_B_PROVIDER_INTERNAL_SESSION_KEYS
    )


def _patch33_revb_sanitize_provider_value(value: Any, prefix: str, removed: List[str]) -> Any:
    if isinstance(value, list):
        return [_patch33_revb_sanitize_provider_value(item, prefix, removed) for item in value]
    if not isinstance(value, dict):
        return value

    out: Dict[str, Any] = {}
    for key, nested in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if _patch33_revb_is_internal_provider_session_key(key):
            removed.append(path)
            continue
        out[key] = _patch33_revb_sanitize_provider_value(nested, path, removed)
    return out


def _patch33_revb_sanitize_provider_payload(payload: Any) -> Tuple[Dict[str, Any], List[str]]:
    """Remove Orkio-only manual/team context before calling Realtime provider.

    PATCH 33 REV B keeps internal orchestration fields available in events:batch,
    meeting_state and logs, but guarantees client_secrets/session payloads do not
    contain provider-invalid keys such as session.manual_agent_lock.
    """

    if not isinstance(payload, dict):
        return {}, ["payload"]

    removed: List[str] = []
    safe_payload = _patch33_revb_sanitize_provider_value(dict(payload), "", removed)
    unique_removed = sorted(set(str(item or "") for item in removed if str(item or "").strip()))
    return safe_payload if isinstance(safe_payload, dict) else {}, unique_removed



def _patch32_revf_event_payloads(event: Any) -> List[Dict[str, Any]]:
    """Return event/root/meta/payload dicts for manual-button recovery."""
    out: List[Dict[str, Any]] = []
    try:
        data = _rtb06_event_dict(event)
    except Exception:
        data = {}
    if isinstance(data, dict):
        out.append(data)
        for key in ("meta", "payload", "data"):
            nested = data.get(key)
            if isinstance(nested, dict):
                out.append(nested)
    return out


def _patch32_revf_extract_manual_target_from_events(events: List[Any]) -> str:
    """Recover manual target from telemetry when api/body fields are missing.

    REV F is intentionally defensive: response-authority release telemetry must
    never clear the selected UI button. We only recover positive selections from
    manual authority events and ignore response_authority_lock_released/reset-only
    events.
    """
    for ev in reversed(events or []):
        try:
            event_name = _event_name(ev).strip().lower()
        except Exception:
            event_name = ""
        if "response_authority_lock_released" in event_name or "authority_lock_released" in event_name:
            continue
        for obj in _patch32_revf_event_payloads(ev):
            for key in (
                "manual_target_slug",
                "selected_agent_slug",
                "selected_manual_agent_slug",
                "target_agent_slug",
                "manual_slug",
            ):
                slug = _normalize_realtime_agent_slug(obj.get(key), default="")
                if slug in {"team", "orkio", "orion", "chris", "laura"}:
                    return slug
    return ""


def _patch32_revf_is_empty_meeting_state_payload(state: Any) -> bool:
    if not isinstance(state, dict):
        return False
    active_slug = _normalize_realtime_agent_slug(
        state.get("active_speaker_slug")
        or state.get("active_persona_slug")
        or state.get("target_agent_slug")
        or state.get("visible_agent")
        or "",
        default="",
    )
    participants = state.get("participant_slugs") if isinstance(state.get("participant_slugs"), list) else state.get("participants")
    if not isinstance(participants, list):
        participants = []
    return bool(
        not str(state.get("session_id") or "").strip()
        and not active_slug
        and not str(state.get("active_speaker_name") or state.get("active_agent_name") or "").strip()
        and len(participants) == 0
        and str(state.get("transition_reason") or "").strip().lower() in {"", "state_update"}
        and not str(state.get("response_control") or "").strip()
    )


def _rtb30_latest_user_transcript(events: List[Any]) -> str:
    """Return the latest user transcript.final text for meeting-state authority checks."""
    latest = ""
    for ev in events or []:
        try:
            if _event_name(ev).strip().lower() != "transcript.final":
                continue
            text = _rtb06_extract_final_text(ev)
            if text:
                latest = text
        except Exception:
            continue
    return latest


def _rtb30_state_active_slug(state: Optional[Dict[str, Any]]) -> str:
    state = state if isinstance(state, dict) else {}
    return _normalize_realtime_agent_slug(
        state.get("active_speaker_slug")
        or state.get("active_persona_slug")
        or state.get("target_agent_slug")
        or "",
        default="",
    )


def _rtb30_last_turn_source(state: Optional[Dict[str, Any]]) -> str:
    state = state if isinstance(state, dict) else {}
    last_turn = state.get("last_turn") if isinstance(state.get("last_turn"), dict) else {}
    return str(last_turn.get("source") or "").strip().lower()


def _rtb30_last_turn_kind(state: Optional[Dict[str, Any]]) -> str:
    state = state if isinstance(state, dict) else {}
    last_turn = state.get("last_turn") if isinstance(state.get("last_turn"), dict) else {}
    return str(last_turn.get("kind") or last_turn.get("transition_reason") or "").strip().lower()


def _rtb30_is_server_resolved_state(state: Optional[Dict[str, Any]]) -> bool:
    """True when backend/router has resolved an authoritative speaker for the room."""
    active_slug = _rtb30_state_active_slug(state)
    if not active_slug:
        return False
    source = _rtb30_last_turn_source(state)
    kind = _rtb30_last_turn_kind(state)
    return bool(
        source == "meeting_orchestrator"
        or kind in {
            "handoff",
            "addressed_turn",
            "direct_address",
            "command_address",
            "multi_agent_sequence",
            "team_panel",
            "readonly_audit",
        }
    )


def _rtb30_should_quarantine_client_echo(
    state: Optional[Dict[str, Any]],
    incoming_agent_slug: Any,
) -> Tuple[bool, str, str]:
    """Prevent stale frontend echoes from overriding the server-resolved speaker.

    The PATCH 29 logs showed a direct address resolving Laura correctly and then
    a later client_state_echo restoring Orion. The client payload remains useful
    as telemetry, but it must not be allowed to replace an authoritative server
    handoff/persona decision.
    """
    preserved_slug = _rtb30_state_active_slug(state)
    incoming_slug = _normalize_realtime_agent_slug(incoming_agent_slug, default="")
    if not preserved_slug or not incoming_slug:
        return False, incoming_slug, preserved_slug
    if incoming_slug == preserved_slug:
        return False, incoming_slug, preserved_slug
    if not _rtb30_is_server_resolved_state(state):
        return False, incoming_slug, preserved_slug
    return True, incoming_slug, preserved_slug


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
            "patch": "RTB06_V8",
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


def _rtb06_event_agent_hint(event: Any, session_ctx: Dict[str, Any], text: str) -> str:
    data = _rtb06_event_dict(event)
    event_name = _event_name(event).lower()
    session_meeting_state = session_ctx.get("meeting_state") if isinstance(session_ctx, dict) else None
    meeting_authority_slug = _normalize_realtime_agent_slug(
        session_ctx.get("meeting_active_speaker_slug")
        or session_ctx.get("meeting_active_persona_slug")
        or (session_meeting_state.get("active_speaker_slug") if isinstance(session_meeting_state, dict) else "")
        or (session_meeting_state.get("active_persona_slug") if isinstance(session_meeting_state, dict) else ""),
        default="",
    )
    if event_name in {"response.final", "response.done", "assistant.final"} and meeting_authority_slug:
        return meeting_authority_slug

    candidates: List[Any] = []

    def add_from(obj: Any) -> None:
        if not isinstance(obj, dict):
            return
        for key in (
            "agent_name",
            "speaker_name",
            "visible_agent",
            "active_agent",
            "target_agent_slug",
            "agent_id",
            "speaker",
        ):
            value = obj.get(key)
            if value:
                candidates.append(value)

    add_from(data)
    add_from(data.get("meta") if isinstance(data, dict) else None)
    add_from(data.get("payload") if isinstance(data, dict) else None)
    add_from(session_ctx)

    for candidate in candidates:
        slug = _normalize_realtime_agent_slug(candidate, default="")
        if slug:
            return slug

    # Only infer from the assistant text when it clearly declares the identity.
    raw = str(text or "").strip().lower()
    if re.search(r"\b(sou|eu sou|aqui e|aqui é|fala)\s+(o\s+)?orion\b", raw, re.I):
        return "orion"
    if re.search(r"\b(sou|eu sou|aqui e|aqui é|fala)\s+(a\s+)?chris\b", raw, re.I):
        return "chris"
    if re.search(r"\b(sou|eu sou|aqui e|aqui é|fala)\s+(a\s+)?laura\b", raw, re.I):
        return "laura"
    if re.search(r"\b(sou|eu sou|aqui e|aqui é|fala)\s+(o\s+)?auditor\b", raw, re.I):
        return "auditor"
    if re.search(r"\b(sou|eu sou|aqui e|aqui é|fala)\s+(o\s+)?team\b", raw, re.I):
        return "team"

    return "orkio"


def _rtb06_agent_name_for_event(event: Any, session_ctx: Dict[str, Any], text: str) -> str:
    slug = _rtb06_event_agent_hint(event, session_ctx, text)
    return _agent_display_name_from_slug(slug)


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
            agent_name=(_rtb06_agent_name_for_event(ev, session_ctx, text) if role == "assistant" else None),
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



def _rtb07_orchestration_bridge_candidate(
    *,
    session_id: str,
    events: List[Any],
    promotion: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Detect voice turns that should be bridged into the governed text orchestrator.

    This does not execute patches or deploys. It only asks the frontend to route
    the final transcript through the normal chat stream, where @Orion/@Team
    governance already exists.
    """

    if not session_id or not events:
        return None

    latest_text = ""
    for ev in events:
        event_name = _event_name(ev).strip().lower()
        if event_name != "transcript.final":
            continue
        text = _rtb06_extract_final_text(ev)
        if text:
            latest_text = text

    if not latest_text:
        return None

    normalized = (
        latest_text
        .lower()
        .replace("á", "a")
        .replace("à", "a")
        .replace("ã", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )

    intent = bool(re.search(
        r"\b(auditoria|read\s*-?\s*only|readonly|war\s*room|orquestrac[aã]o|orquestracao|realtime|real\s*time|agentes?|orion|chris|diagnostico|logs?|runtime|backend|frontend)\b",
        normalized,
        re.I,
    ))
    if not intent:
        return None

    return {
        "status": "candidate",
        "session_id": session_id,
        "thread_id": (promotion or {}).get("thread_id"),
        "text": latest_text,
        "route_family": "realtime_voice_orchestration_audit",
        "target_agent": "Orion",
        "write_allowed": False,
        "patch": "EFATA777_V8",
    }


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
        is_admin = _is_admin_user(user, db_user)
        if is_admin:
            try:
                body.client_controlled_response = True
            except Exception:
                pass

        mode = str(_safe_getattr(body, "mode", "") or "platform").strip().lower()
        response_profile = str(_safe_getattr(body, "response_profile", "") or "natural").strip().lower()
        language_profile = str(
            _safe_getattr(body, "language_profile", None)
            or _safe_getattr(body, "language", None)
            or "pt"
        ).strip().lower() or "pt"

        thread_id = str(_safe_getattr(body, "thread_id", "") or "").strip()
        agent_id = str(_safe_getattr(body, "agent_id", "") or "").strip() or None
        agent_context = _resolve_realtime_agent_context(
            deps,
            db,
            org=org,
            body=body,
            explicit_agent_id=agent_id,
        )

        base_instructions = _build_instructions(
            deps,
            mode=mode,
            response_profile=response_profile,
            language_profile=language_profile,
            agent_context=agent_context,
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
            profile_address_names=_safe_getattr(body, "preferred_address_names", None),
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
                "agent": _json_safe(agent_context),
                "serialization_safe": "RTB03_RTB06_EFATA777_V8",
            }
        )

    @router.post("/api/realtime/start")
    async def realtime_start(
        body: RealtimeStartReq,
        request: Request,
        x_org_slug: Optional[str] = Header(default=None),
        user: Any = Depends(get_current_user),
        db: Any = Depends(get_db),
    ) -> JSONResponse:
        org = _resolve_org_safe(deps, user, x_org_slug)
        db_user = _lookup_db_user(deps, db, user, org)
        uid = str(_safe_getattr(user, "sub", None) or _safe_getattr(user, "id", "") or "").strip() or None
        is_admin = _is_admin_user(user, db_user)
        if is_admin:
            try:
                body.client_controlled_response = True
            except Exception:
                pass

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
        raw_manual_target_slug = (
            str(_safe_getattr(body, "manual_target_slug", "") or "").strip()
            or str(await _request_json_field(request, "manual_target_slug", "") or "").strip()
        )
        manual_target_slug = _normalize_realtime_agent_slug(raw_manual_target_slug, default="")
        body_manual_agent_lock = bool(_safe_getattr(body, "manual_agent_lock", False))
        raw_team_panel_order = (
            _safe_getattr(body, "manual_team_panel_order", None)
            or await _request_json_field(request, "manual_team_panel_order", None)
            or _safe_getattr(body, "target_agent_slugs", None)
            or []
        )
        raw_team_conversation_version = (
            str(_safe_getattr(body, "team_conversation_orchestrator_version", "") or "").strip()
            or str(await _request_json_field(request, "team_conversation_orchestrator_version", "") or "").strip()
        )
        raw_team_conversation_staging_verification_version = (
            str(_safe_getattr(body, "team_conversation_staging_verification_version", "") or "").strip()
            or str(await _request_json_field(request, "team_conversation_staging_verification_version", "") or "").strip()
        )
        raw_team_conversation_mode = (
            str(_safe_getattr(body, "team_conversation_mode", "") or "").strip()
            or str(await _request_json_field(request, "team_conversation_mode", "") or "").strip()
        )
        raw_team_conversation_focus = (
            str(_safe_getattr(body, "manual_team_focus_slug", "") or "").strip()
            or str(await _request_json_field(request, "manual_team_focus_slug", "") or "").strip()
            or str(_safe_getattr(body, "target_agent_slug", "") or "").strip()
            or "orkio"
        )
        manual_team_conversation_active = _patch33_is_team_conversation_active(
            _safe_getattr(body, "manual_team_conversation_active", None),
            await _request_json_field(request, "manual_team_conversation_active", None),
            raw_team_conversation_version,
            raw_team_conversation_mode,
            _safe_getattr(body, "response_control", None),
        )
        team_conversation_focus_slug = _patch33_team_focus_slug(raw_team_conversation_focus, default="orkio")
        raw_team_turn_queue = (
            _safe_getattr(body, "manual_team_turn_queue", None)
            or await _request_json_field(request, "manual_team_turn_queue", None)
            or raw_team_panel_order
        )
        manual_team_panel_order = (
            _patch33_team_turn_queue(raw_team_turn_queue, team_conversation_focus_slug)
            if (manual_target_slug == "team" or manual_team_conversation_active)
            else []
        )
        if body_manual_agent_lock and manual_target_slug:
            try:
                if manual_target_slug == "team" or manual_team_conversation_active:
                    body.target_agent_slug = team_conversation_focus_slug
                    body.visible_agent = "Team"
                    body.dest_mode = "team"
                    body.target_agent_slugs = manual_team_panel_order
                    body.multi_agent_turn = True
                    body.response_control = PATCH_33_TEAM_CONVERSATION_RESPONSE_CONTROL
                    body.manual_team_conversation_active = True
                    body.manual_team_focus_slug = team_conversation_focus_slug
                    body.manual_team_turn_queue = manual_team_panel_order
                    body.team_conversation_mode = PATCH_33_TEAM_CONVERSATION_MODE
                    body.team_conversation_orchestrator_version = PATCH_33_TEAM_CONVERSATION_ORCHESTRATOR_VERSION
                else:
                    body.target_agent_slug = manual_target_slug
                    body.visible_agent = _agent_display_name_from_slug(manual_target_slug)
                    body.dest_mode = "single"
            except Exception:
                pass
        agent_context = _resolve_realtime_agent_context(
            deps,
            db,
            org=org,
            body=body,
            explicit_agent_id=agent_id,
        )
        agent_id = str(agent_context.get("agent_id") or agent_id or "").strip() or None

        base_instructions = _build_instructions(
            deps,
            mode=mode,
            response_profile=response_profile,
            language_profile=language_profile,
            agent_context=agent_context,
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
            profile_address_names=(
                _safe_getattr(body, "preferred_address_names", None)
                or await _request_json_field(request, "preferred_address_names", None)
            ),
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

        initial_meeting_state = build_initial_meeting_state(
            session_id=session_id,
            thread_id=thread_id,
            org=org,
            user_id=uid,
            dest_mode=str(agent_context.get("dest_mode") or _safe_getattr(body, "dest_mode", "") or "team").strip().lower(),
            active_agent_slug=(
                team_conversation_focus_slug if (body_manual_agent_lock and (manual_target_slug == "team" or manual_team_conversation_active)) else (
                    manual_target_slug
                    or agent_context.get("slug")
                    or agent_context.get("agent_slug")
                    or agent_context.get("display_name")
                    or agent_id
                    or "orkio"
                )
            ),
            active_agent_name=(
                _agent_display_name_from_slug(team_conversation_focus_slug) if (body_manual_agent_lock and (manual_target_slug == "team" or manual_team_conversation_active))
                else (_agent_display_name_from_slug(manual_target_slug) if manual_target_slug else (agent_context.get("display_name") or agent_context.get("name") or ""))
            ),
            include_internal=bool(is_admin),
            history_loaded=bool(overlay_meta.get("thread_context_loaded", True)),
            now_ts=started_at,
        )

        initial_meeting_observability = build_meeting_transition_log(
            previous_state={},
            next_state=initial_meeting_state,
            directive={"kind": "session_start", "match_type": "session_start", "session_id": session_id, "thread_id": thread_id},
            source="realtime_start",
            persisted=None,
            now_ts=started_at,
        )

        session_meta = {
            "patch": "RTB03_RTB06_EFATA777_V8_PATCH29",
            "mode": mode,
            "response_profile": response_profile,
            "language_profile": language_profile,
            "context": overlay_meta,
            "agent": _json_safe(agent_context),
            "dest_mode": str(agent_context.get("dest_mode") or _safe_getattr(body, "dest_mode", "") or "").strip().lower(),
            "meeting_orchestrator": {"enabled": True, "kind": "turn_based"},
            "meeting_state": _json_safe(initial_meeting_state),
            "meeting_state_version": MEETING_STATE_VERSION,
            "meeting_observability": _json_safe(summarize_transition_for_response(initial_meeting_observability)),
            "meeting_observability_version": MEETING_OBSERVABILITY_VERSION,
            "client_controlled_response": bool(_safe_getattr(body, "client_controlled_response", False)),
            # PATCH_27_MULTI_AGENT_RESPONSE_CONTROL:
            "target_agent_slugs": _json_safe(_safe_getattr(body, "target_agent_slugs", None) or []),
            "multi_agent_turn": bool(_safe_getattr(body, "multi_agent_turn", False)),
            "response_control": str(_safe_getattr(body, "response_control", "") or "").strip(),
            "manual_agent_lock": bool(_safe_getattr(body, "manual_agent_lock", False)),
            "manual_target_slug": manual_target_slug or None,
            "manual_authority_version": str(
                _safe_getattr(body, "manual_authority_version", "")
                or await _request_json_field(request, "manual_authority_version", "")
                or ""
            ).strip(),
            "manual_authority_source": str(
                _safe_getattr(body, "manual_authority_source", "")
                or await _request_json_field(request, "manual_authority_source", "")
                or ""
            ).strip(),
            "manual_lock_staging_proof_version": str(
                _safe_getattr(body, "manual_lock_staging_proof_version", "")
                or await _request_json_field(request, "manual_lock_staging_proof_version", "")
                or ""
            ).strip(),
            "manual_lock_staging_proof_production_guard_version": str(
                _safe_getattr(body, "manual_lock_staging_proof_production_guard_version", "")
                or await _request_json_field(request, "manual_lock_staging_proof_production_guard_version", "")
                or ""
            ).strip(),
            "manual_team_panel_required": bool(
                _safe_getattr(body, "manual_team_panel_required", False)
                or await _request_json_field(request, "manual_team_panel_required", False)
                or manual_target_slug == "team"
            ),
            "manual_team_panel_order": _json_safe(manual_team_panel_order),
            "manual_team_conversation_active": bool(manual_team_conversation_active),
            "manual_team_focus_slug": team_conversation_focus_slug if manual_team_conversation_active else "",
            "manual_team_turn_queue": _json_safe(manual_team_panel_order if manual_team_conversation_active else []),
            "team_conversation_mode": PATCH_33_TEAM_CONVERSATION_MODE if manual_team_conversation_active else "",
            "team_conversation_orchestrator_version": PATCH_33_TEAM_CONVERSATION_ORCHESTRATOR_VERSION if manual_team_conversation_active else "",
"team_conversation_staging_verification_version": (raw_team_conversation_staging_verification_version or PATCH_33_REV_A_TEAM_CONVERSATION_STAGING_VERIFICATION_VERSION) if manual_team_conversation_active else "",
            "realtime_provider_payload_sanitizer_version": str(
                _safe_getattr(body, "realtime_provider_payload_sanitizer_version", "")
                or await _request_json_field(request, "realtime_provider_payload_sanitizer_version", "")
                or PATCH_33_REV_B_REALTIME_PROVIDER_PAYLOAD_SANITIZER_VERSION
            ).strip(),
            "live_agent_switch_runtime_fix_version": str(
                _safe_getattr(body, "live_agent_switch_runtime_fix_version", "")
                or await _request_json_field(request, "live_agent_switch_runtime_fix_version", "")
                or PATCH_33_REV_C_LIVE_AGENT_SWITCH_RUNTIME_FIX_VERSION
            ).strip(),
            "team_panel_version": str(
                _safe_getattr(body, "team_panel_version", "")
                or await _request_json_field(request, "team_panel_version", "")
                or (PATCH_32_REV_D_TEAM_PANEL_VERSION if manual_target_slug == "team" else "")
            ).strip(),
            "team_panel_mode": str(
                _safe_getattr(body, "team_panel_mode", "")
                or await _request_json_field(request, "team_panel_mode", "")
                or (PATCH_32_REV_D_TEAM_PANEL_MODE if manual_target_slug == "team" else "")
            ).strip(),
            "team_panel_voice_moderator_slug": str(
                _safe_getattr(body, "team_panel_voice_moderator_slug", "")
                or await _request_json_field(request, "team_panel_voice_moderator_slug", "")
                or (PATCH_32_REV_D_TEAM_PANEL_VOICE_MODERATOR_SLUG if manual_target_slug == "team" else "")
            ).strip(),
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
                "agent=%s dest_mode=%s admin=%s founder_identity=%s thread_context=%s messages=%s",
                uid,
                org,
                session_id,
                thread_id,
                agent_context.get("display_name"),
                agent_context.get("dest_mode"),
                bool(is_admin),
                bool(overlay_meta.get("founder_identity_injected")),
                bool(overlay_meta.get("thread_context_loaded")),
                overlay_meta.get("thread_context_messages"),
            )
            logger.warning("EFATA777_V12_MEETING_TRANSITION %s", transition_log_line(initial_meeting_observability))
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
                "agent": _json_safe(agent_context),
                "meeting_state": _json_safe(initial_meeting_state),
                "meeting_state_version": MEETING_STATE_VERSION,
                "meeting_observability": _json_safe(summarize_transition_for_response(initial_meeting_observability)),
                "meeting_observability_version": MEETING_OBSERVABILITY_VERSION,
                "manual_lock_staging_proof_version": session_meta.get("manual_lock_staging_proof_version") or "",
                "manual_lock_staging_proof_production_guard_version": session_meta.get("manual_lock_staging_proof_production_guard_version") or PATCH_32_REV_J_MANUAL_LOCK_STAGING_PROOF_PRODUCTION_GUARD_VERSION,
                "manual_team_conversation_active": bool(session_meta.get("manual_team_conversation_active")),
                "manual_team_focus_slug": session_meta.get("manual_team_focus_slug") or "",
                "manual_team_turn_queue": _json_safe(session_meta.get("manual_team_turn_queue") or []),
                "team_conversation_mode": session_meta.get("team_conversation_mode") or "",
                "team_conversation_orchestrator_version": session_meta.get("team_conversation_orchestrator_version") or "",
"team_conversation_staging_verification_version": session_meta.get("team_conversation_staging_verification_version") or "",
                "realtime_provider_payload_sanitizer_version": session_meta.get("realtime_provider_payload_sanitizer_version") or PATCH_33_REV_B_REALTIME_PROVIDER_PAYLOAD_SANITIZER_VERSION,
                "live_agent_switch_runtime_fix_version": session_meta.get("live_agent_switch_runtime_fix_version") or PATCH_33_REV_C_LIVE_AGENT_SWITCH_RUNTIME_FIX_VERSION,
                "serialization_safe": "RTB03_RTB06_EFATA777_V8_PATCH29",
                "timebox_policy": "advisory_only_esg",
            }
        )

    @router.post("/api/realtime/events:batch")
    async def realtime_events_batch(
        body: RealtimeEventsBatchReq,
        request: Request,
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

        bridge = _rtb07_orchestration_bridge_candidate(
            session_id=session_id,
            events=events,
            promotion=promotion,
        )

        meeting_directive = None
        meeting_state: Dict[str, Any] = {}
        meeting_state_persisted = False
        meeting_transition: Dict[str, Any] = {}
        body_manual_lock_staging_proof_version = ""
        body_manual_lock_staging_proof_production_guard_version = ""
        try:
            session_ctx = _rtb06_get_session_context(
                deps,
                db,
                session_id=session_id,
                fallback_org=org,
                fallback_user_id=uid,
            )
            body_target_agent_slug = str(_safe_getattr(body, "target_agent_slug", "") or "").strip()
            event_manual_target_slug = _patch32_revf_extract_manual_target_from_events(events)
            body_manual_target_raw = (
                str(_safe_getattr(body, "manual_target_slug", "") or "").strip()
                or str(await _request_json_field(request, "manual_target_slug", "") or "").strip()
                or event_manual_target_slug
            )
            body_manual_target_slug = _normalize_realtime_agent_slug(body_manual_target_raw, default="")
            body_visible_agent = str(_safe_getattr(body, "visible_agent", "") or "").strip()
            body_agent_id = str(_safe_getattr(body, "agent_id", "") or "").strip()
            body_dest_mode = str(_safe_getattr(body, "dest_mode", "") or "").strip().lower()
            body_meeting_state = _safe_getattr(body, "meeting_state", None)
            if _patch32_revf_is_empty_meeting_state_payload(body_meeting_state):
                try:
                    logger.warning(
                        "PATCH32_REV_F_EMPTY_MEETING_STATE_IGNORED session_id=%s manual_agent_lock=%s manual_target_slug=%s event_manual_target_slug=%s version=%s",
                        session_id,
                        bool(_safe_getattr(body, "manual_agent_lock", False) or event_manual_target_slug),
                        body_manual_target_slug or body_manual_target_raw or "",
                        event_manual_target_slug or "",
                        PATCH_32_REV_F_MANUAL_BUTTON_LOCK_PERSISTENCE_VERSION,
                    )
                except Exception:
                    pass
                body_meeting_state = None
            if isinstance(body_meeting_state, dict):
                state_session_id = str(body_meeting_state.get("session_id") or "").strip()
                if state_session_id and state_session_id != session_id:
                    try:
                        logger.warning(
                            "PATCH32_REV_C_STALE_SESSION_STATE_IGNORED session_id=%s stale_session_id=%s manual_agent_lock=%s manual_target_slug=%s",
                            session_id,
                            state_session_id,
                            bool(_safe_getattr(body, "manual_agent_lock", False)),
                            body_manual_target_slug or body_manual_target_raw or "",
                        )
                    except Exception:
                        pass
                    body_meeting_state = None
            body_target_agent_slugs = [
                str(slug or "").strip().lower()
                for slug in (_safe_getattr(body, "target_agent_slugs", None) or [])
                if str(slug or "").strip()
            ]
            body_multi_agent_turn = bool(_safe_getattr(body, "multi_agent_turn", False))
            body_response_control = str(_safe_getattr(body, "response_control", "") or "").strip()
            body_team_conversation_version = str(
                _safe_getattr(body, "team_conversation_orchestrator_version", "")
                or await _request_json_field(request, "team_conversation_orchestrator_version", "")
                or ""
            ).strip()
            body_team_conversation_staging_verification_version = str(
                _safe_getattr(body, "team_conversation_staging_verification_version", "")
                or await _request_json_field(request, "team_conversation_staging_verification_version", "")
                or ""
            ).strip()
            body_team_conversation_mode = str(
                _safe_getattr(body, "team_conversation_mode", "")
                or await _request_json_field(request, "team_conversation_mode", "")
                or ""
            ).strip()
            body_manual_team_focus_slug = _patch33_team_focus_slug(
                _safe_getattr(body, "manual_team_focus_slug", None)
                or await _request_json_field(request, "manual_team_focus_slug", None)
                or body_target_agent_slug
                or "orkio",
                default="orkio",
            )
            body_manual_team_conversation_active = _patch33_is_team_conversation_active(
                _safe_getattr(body, "manual_team_conversation_active", None),
                await _request_json_field(request, "manual_team_conversation_active", None),
                body_team_conversation_version,
                body_team_conversation_mode,
                body_response_control,
            )
            if body_manual_team_conversation_active:
                body_manual_target_slug = "team"
                body_response_control = PATCH_33_TEAM_CONVERSATION_RESPONSE_CONTROL
                body_multi_agent_turn = True
            body_manual_team_panel_order = _patch33_team_turn_queue(
                _safe_getattr(body, "manual_team_turn_queue", None)
                or await _request_json_field(request, "manual_team_turn_queue", None)
                or _safe_getattr(body, "manual_team_panel_order", None)
                or await _request_json_field(request, "manual_team_panel_order", None)
                or body_target_agent_slugs,
                body_manual_team_focus_slug,
            ) if (body_manual_target_slug == "team" or body_manual_team_conversation_active) else []
            # original PATCH_32_REV_D order fallback remains below for non-PATCH_33 payloads
            body_manual_team_panel_order = body_manual_team_panel_order or _coerce_manual_team_panel_order(
                _safe_getattr(body, "manual_team_panel_order", None)
                or await _request_json_field(request, "manual_team_panel_order", None)
                or body_target_agent_slugs
            ) if body_manual_target_slug == "team" else []
            body_manual_team_panel_required = bool(
                _safe_getattr(body, "manual_team_panel_required", False)
                or await _request_json_field(request, "manual_team_panel_required", False)
                or body_manual_target_slug == "team"
                or body_manual_team_conversation_active
            )
            body_team_panel_version = str(
                _safe_getattr(body, "team_panel_version", "")
                or await _request_json_field(request, "team_panel_version", "")
                or (PATCH_32_REV_D_TEAM_PANEL_VERSION if (body_manual_target_slug == "team" or body_manual_team_conversation_active) else "")
            ).strip()
            body_team_panel_mode = str(
                _safe_getattr(body, "team_panel_mode", "")
                or await _request_json_field(request, "team_panel_mode", "")
                or (PATCH_33_TEAM_CONVERSATION_MODE if body_manual_team_conversation_active else (PATCH_32_REV_D_TEAM_PANEL_MODE if body_manual_target_slug == "team" else ""))
            ).strip()
            body_team_panel_voice_moderator_slug = str(
                _safe_getattr(body, "team_panel_voice_moderator_slug", "")
                or await _request_json_field(request, "team_panel_voice_moderator_slug", "")
                or (body_manual_team_focus_slug if body_manual_team_conversation_active else (PATCH_32_REV_D_TEAM_PANEL_VOICE_MODERATOR_SLUG if body_manual_target_slug == "team" else ""))
            ).strip()
            body_manual_agent_lock = bool(_safe_getattr(body, "manual_agent_lock", False) or event_manual_target_slug)
            body_manual_authority_version = str(_safe_getattr(body, "manual_authority_version", "") or "").strip()
            body_manual_sticky_state_version = str(
                _safe_getattr(body, "manual_sticky_state_version", "")
                or await _request_json_field(request, "manual_sticky_state_version", "")
                or ""
            ).strip()
            body_manual_lock_persistence_version = str(
                _safe_getattr(body, "manual_lock_persistence_version", "")
                or await _request_json_field(request, "manual_lock_persistence_version", "")
                or ""
            ).strip()
            body_manual_lock_staging_proof_version = str(
                _safe_getattr(body, "manual_lock_staging_proof_version", "")
                or await _request_json_field(request, "manual_lock_staging_proof_version", "")
                or ""
            ).strip()
            body_manual_lock_staging_proof_production_guard_version = str(
                _safe_getattr(body, "manual_lock_staging_proof_production_guard_version", "")
                or await _request_json_field(request, "manual_lock_staging_proof_production_guard_version", "")
                or ""
            ).strip()
            body_auto_handoff_enabled = _safe_getattr(body, "auto_handoff_enabled", None)
            body_manual_authority_active = bool(
                body_manual_agent_lock
                or body_manual_target_slug
                or body_response_control.startswith("manual_")
                or body_manual_authority_version.startswith("PATCH_32")
                or body_manual_sticky_state_version.startswith("PATCH_32_REV_E")
                or body_manual_lock_persistence_version.startswith("PATCH_32_REV_F")
                or body_manual_lock_staging_proof_version.startswith("PATCH_32_REV_H")
                or body_manual_lock_staging_proof_production_guard_version.startswith("PATCH_32_REV_J")
                or body_manual_team_conversation_active
                or body_team_conversation_version.startswith("PATCH_33")
                or body_response_control == PATCH_33_TEAM_CONVERSATION_RESPONSE_CONTROL
                or body_auto_handoff_enabled is False
            )
            existing_meeting_state = _merge_client_meeting_state(
                session_ctx.get("meeting_state") if isinstance(session_ctx.get("meeting_state"), dict) else {},
                body_meeting_state if isinstance(body_meeting_state, dict) else {},
            )
            latest_user_transcript_for_meeting = _rtb30_latest_user_transcript(events)

            # PATCH 30:
            # The backend meeting state is the authority for the current speaker.
            # body_target_agent_slug/body_visible_agent are client echoes and can be
            # stale after a server-side handoff. Use them only when no server active
            # speaker exists yet.
            server_active_agent_slug = (
                _rtb30_state_active_slug(existing_meeting_state)
                or session_ctx.get("meeting_active_speaker_slug")
                or session_ctx.get("agent_slug")
                or session_ctx.get("agent_id")
                or ""
            )
            client_echo_agent_slug = (
                body_target_agent_slug
                or body_visible_agent
                or body_agent_id
                or ""
            )
            current_agent_slug = (
                server_active_agent_slug
                or client_echo_agent_slug
                or ""
            )
            effective_dest_mode = body_dest_mode or session_ctx.get("dest_mode") or "team"
            manual_lock_invalid = False

            if body_manual_authority_active and (latest_user_transcript_for_meeting or body_manual_target_slug):
                # PATCH 32:
                # Manual button authority intentionally suppresses natural-language
                # handoff/direct-address routing. The selected UI button is the source
                # of truth for the current realtime turn.
                if body_manual_agent_lock and not body_manual_target_slug:
                    manual_lock_invalid = True
                    meeting_state = existing_meeting_state if isinstance(existing_meeting_state, dict) else {}
                    try:
                        logger.warning(
                            "PATCH32_REV_C_MANUAL_LOCK_MISSING_TARGET session_id=%s manual_agent_lock=%s manual_target_slug=%s active_speaker_slug=%s active_persona_slug=%s target_agent_slug=%s target_agent_slugs=%s response_control=%s match_type=%s transition_reason=%s",
                            session_id,
                            True,
                            body_manual_target_raw or "",
                            meeting_state.get("active_speaker_slug") if isinstance(meeting_state, dict) else "",
                            meeting_state.get("active_persona_slug") if isinstance(meeting_state, dict) else "",
                            meeting_state.get("target_agent_slug") if isinstance(meeting_state, dict) else "",
                            meeting_state.get("target_agent_slugs") if isinstance(meeting_state, dict) else [],
                            body_response_control,
                            "manual_lock_invalid",
                            "manual_lock_missing_target",
                        )
                    except Exception:
                        pass
                else:
                    manual_target_slug = body_manual_target_slug
                    if manual_target_slug == "team":
                        manual_target_slugs = body_manual_team_panel_order or _coerce_manual_team_panel_order(body_target_agent_slugs)
                        meeting_directive = {
                            "status": "directive",
                            "kind": "manual_team_conversation",
                            "match_type": "manual_team_conversation",
                            "transition_reason": "manual_team_conversation",
                            "target_agent_slug": body_manual_team_focus_slug if body_manual_team_conversation_active else "team",
                            "target_agent_slugs": manual_target_slugs,
                            "multi_agent_turn": True,
                            "response_control": PATCH_33_TEAM_CONVERSATION_RESPONSE_CONTROL if body_manual_team_conversation_active else "manual_team_panel",
                            "confidence": 1.0,
                            "dedupe_key": f"{session_id}:manual:team:{body_manual_team_focus_slug if body_manual_team_conversation_active else 'team'}:{latest_user_transcript_for_meeting[:160]}",
                            "manual_agent_lock": True,
                            "manual_target_slug": "team",
                            "manual_authority_version": PATCH_32_REV_C_MANUAL_TARGET_SOURCE_OF_TRUTH_VERSION,
                            "manual_sticky_state_version": PATCH_32_REV_E_MANUAL_BUTTON_STICKY_STATE_VERSION,
                            "manual_lock_persistence_version": PATCH_32_REV_F_MANUAL_BUTTON_LOCK_PERSISTENCE_VERSION,
                            "manual_lock_staging_proof_version": body_manual_lock_staging_proof_version or PATCH_32_REV_H_MANUAL_LOCK_STAGING_PROOF_VERSION,
                            "manual_lock_staging_proof_production_guard_version": body_manual_lock_staging_proof_production_guard_version or PATCH_32_REV_J_MANUAL_LOCK_STAGING_PROOF_PRODUCTION_GUARD_VERSION,
                            "session_voice_sync_version": PATCH_32_PREDEPLOY_PREMIUM_VERSION,
                            "manual_button_authority": True,
                            "should_create_response": False,
                            "manual_team_panel_required": True,
                            "manual_team_panel_order": manual_target_slugs,
                            "team_panel_version": body_team_panel_version or PATCH_32_REV_D_TEAM_PANEL_VERSION,
                            "team_panel_mode": body_team_panel_mode or PATCH_32_REV_D_TEAM_PANEL_MODE,
                            "team_panel_voice_moderator_slug": body_team_panel_voice_moderator_slug or PATCH_32_REV_D_TEAM_PANEL_VOICE_MODERATOR_SLUG,
                            "manual_team_conversation_active": bool(body_manual_team_conversation_active),
                            "manual_team_focus_slug": body_manual_team_focus_slug if body_manual_team_conversation_active else "",
                            "manual_team_turn_queue": manual_target_slugs,
                            "team_conversation_mode": PATCH_33_TEAM_CONVERSATION_MODE if body_manual_team_conversation_active else "",
                            "team_conversation_orchestrator_version": PATCH_33_TEAM_CONVERSATION_ORCHESTRATOR_VERSION if body_manual_team_conversation_active else "",
"team_conversation_staging_verification_version": (body_team_conversation_staging_verification_version or PATCH_33_REV_A_TEAM_CONVERSATION_STAGING_VERIFICATION_VERSION) if body_manual_team_conversation_active else "",
                        }
                        try:
                            logger.warning(
                                "PATCH32_REV_C_TEAM_HF4C_BYPASS session_id=%s manual_agent_lock=%s manual_target_slug=%s active_speaker_slug=%s active_persona_slug=%s target_agent_slug=%s target_agent_slugs=%s response_control=%s match_type=%s transition_reason=%s",
                                session_id,
                                True,
                                "team",
                                "team",
                                "team",
                                "team",
                                json.dumps(manual_target_slugs, ensure_ascii=False),
                                "manual_team_panel",
                                "manual_team_button",
                                "manual_team_button",
                            )
                            logger.warning(
                                "PATCH32_REV_D_TEAM_PANEL_PRESTAGING session_id=%s team_panel_version=%s manual_team_panel_order=%s manual_team_panel_required=%s voice_moderator=%s",
                                session_id,
                                body_team_panel_version or PATCH_32_REV_D_TEAM_PANEL_VERSION,
                                json.dumps(manual_target_slugs, ensure_ascii=False),
                                True,
                                body_team_panel_voice_moderator_slug or PATCH_32_REV_D_TEAM_PANEL_VOICE_MODERATOR_SLUG,
                            )
                        except Exception:
                            pass
                    else:
                        meeting_directive = {
                            "status": "directive",
                            "kind": "manual_agent_button",
                            "match_type": "manual_agent_button",
                            "transition_reason": "manual_agent_button",
                            "target_agent_slug": manual_target_slug,
                            "target_agent_slugs": [manual_target_slug],
                            "multi_agent_turn": False,
                            "response_control": "manual_agent_authority_single",
                            "confidence": 1.0,
                            "dedupe_key": f"{session_id}:manual:{manual_target_slug}:{latest_user_transcript_for_meeting[:160]}",
                            "manual_agent_lock": True,
                            "manual_target_slug": manual_target_slug,
                            "manual_authority_version": PATCH_32_REV_C_MANUAL_TARGET_SOURCE_OF_TRUTH_VERSION,
                            "manual_sticky_state_version": PATCH_32_REV_E_MANUAL_BUTTON_STICKY_STATE_VERSION,
                            "manual_lock_persistence_version": PATCH_32_REV_F_MANUAL_BUTTON_LOCK_PERSISTENCE_VERSION,
                            "manual_lock_staging_proof_version": body_manual_lock_staging_proof_version or PATCH_32_REV_H_MANUAL_LOCK_STAGING_PROOF_VERSION,
                            "manual_lock_staging_proof_production_guard_version": body_manual_lock_staging_proof_production_guard_version or PATCH_32_REV_J_MANUAL_LOCK_STAGING_PROOF_PRODUCTION_GUARD_VERSION,
                            "session_voice_sync_version": PATCH_32_PREDEPLOY_PREMIUM_VERSION,
                            "manual_button_authority": True,
                            "should_create_response": False,
                        }
                    if meeting_directive:
                        try:
                            logger.warning(
                                "PATCH32_REV_C_MANUAL_TARGET_AUTHORITY session_id=%s manual_agent_lock=%s manual_target_slug=%s active_speaker_slug=%s active_persona_slug=%s target_agent_slug=%s target_agent_slugs=%s response_control=%s match_type=%s transition_reason=%s",
                                session_id,
                                True,
                                manual_target_slug,
                                manual_target_slug,
                                manual_target_slug,
                                meeting_directive.get("target_agent_slug"),
                                json.dumps(meeting_directive.get("target_agent_slugs") or [], ensure_ascii=False),
                                meeting_directive.get("response_control"),
                                meeting_directive.get("match_type"),
                                meeting_directive.get("transition_reason"),
                            )
                        except Exception:
                            pass
            else:
                meeting_directive = build_meeting_directive(
                    session_id=session_id,
                    events=events,
                    current_agent_slug=current_agent_slug,
                    dest_mode=effective_dest_mode,
                    promotion=promotion,
                )

            if meeting_directive:
                if body_target_agent_slugs and not meeting_directive.get("target_agent_slugs"):
                    meeting_directive["target_agent_slugs"] = body_target_agent_slugs
                if body_multi_agent_turn:
                    meeting_directive["multi_agent_turn"] = True
                    meeting_directive["response_control"] = body_response_control or meeting_directive.get("response_control") or "sequenced_team_turns"
                meeting_state = update_meeting_state_from_directive(
                    existing_meeting_state,
                    meeting_directive,
                    session_id=session_id,
                    thread_id=session_ctx.get("thread_id"),
                    org=org,
                    user_id=uid,
                    dest_mode=effective_dest_mode,
                    include_internal=bool(_is_admin_user(user, None)),
                    now_ts=_now_ts(),
                )
                try:
                    meeting_directive["meeting_state"] = _json_safe(meeting_state)
                    meeting_directive["meeting_state_version"] = MEETING_STATE_VERSION
                except Exception:
                    pass
            elif manual_lock_invalid:
                meeting_state = existing_meeting_state if isinstance(existing_meeting_state, dict) else {}
            else:
                quarantine_echo, incoming_echo_slug, preserved_echo_slug = _rtb30_should_quarantine_client_echo(
                    existing_meeting_state,
                    client_echo_agent_slug,
                )

                if not latest_user_transcript_for_meeting:
                    # Telemetry/audio/provider batches are not user turns. They must
                    # not increment turn_index and must not change speaker/persona.
                    meeting_state = existing_meeting_state if isinstance(existing_meeting_state, dict) else {}
                    if quarantine_echo:
                        try:
                            logger.warning(
                                "PATCH30_CLIENT_STATE_ECHO_QUARANTINED session_id=%s incoming=%s preserved=%s reason=no_user_transcript source=events_batch version=%s",
                                session_id,
                                incoming_echo_slug,
                                preserved_echo_slug,
                                PATCH_30_SERVER_SPEAKER_AUTHORITY_VERSION,
                            )
                        except Exception:
                            pass
                else:
                    echo_target_slug = preserved_echo_slug if quarantine_echo else current_agent_slug
                    echo_kind = "client_state_echo_quarantined" if quarantine_echo else "client_state_echo"
                    if quarantine_echo:
                        try:
                            logger.warning(
                                "PATCH30_CLIENT_STATE_ECHO_QUARANTINED session_id=%s incoming=%s preserved=%s reason=server_authority_wins source=events_batch version=%s",
                                session_id,
                                incoming_echo_slug,
                                preserved_echo_slug,
                                PATCH_30_SERVER_SPEAKER_AUTHORITY_VERSION,
                            )
                        except Exception:
                            pass

                    meeting_state = apply_turn_to_meeting_state(
                        existing_meeting_state,
                        session_id=session_id,
                        thread_id=session_ctx.get("thread_id"),
                        org=org,
                        user_id=uid,
                        dest_mode=effective_dest_mode,
                        target_agent_slug=echo_target_slug,
                        target_agent_name=_agent_display_name_from_slug(echo_target_slug) if echo_target_slug else body_visible_agent,
                        kind=echo_kind,
                        source="events_batch",
                        transcript=latest_user_transcript_for_meeting,
                        include_internal=bool(_is_admin_user(user, None)),
                        now_ts=_now_ts(),
                    )

            meeting_state_persisted = _maybe_update_realtime_session_meeting_state(
                deps,
                db,
                session_id=session_id,
                meeting_state=meeting_state,
                logger=logger,
            )

            meeting_transition = build_meeting_transition_log(
                previous_state=existing_meeting_state,
                next_state=meeting_state,
                directive=meeting_directive,
                source="events_batch",
                persisted=meeting_state_persisted,
                now_ts=_now_ts(),
            )

            try:
                patch33_actual_targets = list((meeting_directive or {}).get("target_agent_slugs") or [])
                patch33_required_targets = list(PATCH_32_REV_D_TEAM_PANEL_ORDER)
                patch33_manual_target = str((meeting_directive or {}).get("manual_target_slug") or body_manual_target_slug or "").strip()
                patch33_response_control = str((meeting_directive or {}).get("response_control") or body_response_control or "").strip()
                patch33_multi_agent_turn = bool((meeting_directive or {}).get("multi_agent_turn") or body_multi_agent_turn)
                patch33_team_active = bool((meeting_directive or {}).get("manual_team_conversation_active") or body_manual_team_conversation_active)
                patch33_verification_pass = bool(
                    patch33_manual_target == "team"
                    and patch33_team_active
                    and patch33_multi_agent_turn
                    and patch33_response_control == PATCH_33_TEAM_CONVERSATION_RESPONSE_CONTROL
                    and set(patch33_required_targets).issubset(set(patch33_actual_targets or []))
                )
                if patch33_manual_target == "team" or patch33_team_active or patch33_response_control == PATCH_33_TEAM_CONVERSATION_RESPONSE_CONTROL:
                    logger.warning(
                        "PATCH33_REV_A_TEAM_STAGING_VERIFICATION session_id=%s manual_target_slug=%s manual_team_conversation_active=%s multi_agent_turn=%s response_control=%s target_agent_slugs=%s actual_turn_queue=%s verification_status=%s version=%s",
                        session_id,
                        "team",
                        bool(patch33_team_active),
                        bool(patch33_multi_agent_turn),
                        PATCH_33_TEAM_CONVERSATION_RESPONSE_CONTROL if patch33_response_control == PATCH_33_TEAM_CONVERSATION_RESPONSE_CONTROL else patch33_response_control,
                        json.dumps(patch33_required_targets, ensure_ascii=False),
                        json.dumps(patch33_actual_targets, ensure_ascii=False),
                        "PASS" if patch33_verification_pass else "FAIL",
                        body_team_conversation_staging_verification_version or PATCH_33_REV_A_TEAM_CONVERSATION_STAGING_VERIFICATION_VERSION,
                    )
            except Exception:
                pass

            try:
                logger.warning(
                    "EFATA777_V8_MEETING_DIRECTIVE %s state=%s persisted=%s",
                    json.dumps(summarize_directive_for_log(meeting_directive), ensure_ascii=False, sort_keys=True),
                    json.dumps(summarize_meeting_state_for_log(meeting_state), ensure_ascii=False, sort_keys=True),
                    bool(meeting_state_persisted),
                )
                logger.warning("EFATA777_V12_MEETING_TRANSITION %s", transition_log_line(meeting_transition))
            except Exception:
                pass
        except Exception as meeting_err:
            meeting_directive = None
            try:
                logger.warning("EFATA777_V8_MEETING_DIRECTIVE_FAILED %s", meeting_err)
            except Exception:
                pass

        return {
            "ok": True,
            "session_id": session_id,
            "received": len(events),
            "rtb03": True,
            "rtb06": True,
            "rtb07": True,
            "rtb08_meeting": True,
            "rtb09_meeting_state": True,
            "finals_promoted": promotion,
            "rtb02_bridge": bridge,
            "meeting_orchestrator": meeting_directive,
            "meeting_state": _json_safe(meeting_state),
            "meeting_state_version": MEETING_STATE_VERSION,
            "meeting_observability": _json_safe(summarize_transition_for_response(meeting_transition)),
            "meeting_observability_version": MEETING_OBSERVABILITY_VERSION,
            "team_panel_version": PATCH_32_REV_D_TEAM_PANEL_VERSION,
            "manual_lock_persistence_version": PATCH_32_REV_F_MANUAL_BUTTON_LOCK_PERSISTENCE_VERSION,
            "manual_lock_staging_proof_version": body_manual_lock_staging_proof_version or PATCH_32_REV_H_MANUAL_LOCK_STAGING_PROOF_VERSION,
            "manual_lock_staging_proof_production_guard_version": body_manual_lock_staging_proof_production_guard_version or PATCH_32_REV_J_MANUAL_LOCK_STAGING_PROOF_PRODUCTION_GUARD_VERSION,
            "speaker_authority_version": PATCH_30_SERVER_SPEAKER_AUTHORITY_VERSION,
            "meeting_state_persisted": bool(meeting_state_persisted),
"team_conversation_staging_verification_version": body_team_conversation_staging_verification_version or PATCH_33_REV_A_TEAM_CONVERSATION_STAGING_VERIFICATION_VERSION,
        }

    @router.get("/api/realtime/sessions/{session_id}")
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

        session_ctx = _rtb06_get_session_context(
            deps,
            db,
            session_id=session_id_clean,
            fallback_org=org,
            fallback_user_id=str(_safe_getattr(user, "sub", None) or _safe_getattr(user, "id", "") or "").strip() or None,
        )
        meeting_state = session_ctx.get("meeting_state") if isinstance(session_ctx.get("meeting_state"), dict) else {}

        payload = {
            "ok": True,
            "session_id": session_id_clean,
            "org": org,
            "finals_only": bool(finals_only),
            "session": _json_safe(snapshot) if snapshot else None,
            "meeting_state": _json_safe(meeting_state),
            "meeting_state_version": MEETING_STATE_VERSION,
            "meeting_observability": _json_safe(summarize_transition_for_response(build_meeting_transition_log(
                previous_state={},
                next_state=meeting_state,
                directive={"kind": "session_snapshot", "match_type": "session_snapshot", "session_id": session_id_clean},
                source="realtime_get_session",
                persisted=True,
                now_ts=_now_ts(),
            ))),
            "meeting_observability_version": MEETING_OBSERVABILITY_VERSION,
            "finals": {
                "user_text": "",
                "assistant_text": "",
                "turns": [],
            },
            "rtb03": True,
            "rtb09_meeting_state": True,
            "serialization_safe": "RTB03_RTB06_PATCH25",
            "compatibility_endpoint": "GET /api/realtime/{session_id} | GET /api/realtime/sessions/{session_id}",
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
