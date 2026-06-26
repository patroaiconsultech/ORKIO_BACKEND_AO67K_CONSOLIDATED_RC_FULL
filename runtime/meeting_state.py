# PATCH_25_MEETING_STATE_PERSISTENTE
# PATCH_28_PERSONA_ISOLATION_AND_REGISTRY_DRIVEN_TEAM_PANEL
# Dependency-free meeting state helpers for the Patroai realtime agent room.
#
# Purpose:
# - Persist the room state inside RealtimeSession.meta without migrations.
# - Keep Team as the room and the addressed agent as the active speaker.
# - Preserve participants, active speaker, last speaker and turn count across
#   /api/realtime/start, /api/realtime/events:batch and /api/realtime/{session_id}.

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional

try:  # Runtime package import
    from app.runtime.agent_registry import (
        AGENT_REGISTRY_VERSION,
        CANONICAL_AGENT_REGISTRY,
        agent_display_name,
        canonical_agent_slug,
        ordered_registry_slugs,
        persona_contract,
        team_default_member_slugs,
    )
except Exception:  # pragma: no cover - local package fallback for tests
    from .agent_registry import (
        AGENT_REGISTRY_VERSION,
        CANONICAL_AGENT_REGISTRY,
        agent_display_name,
        canonical_agent_slug,
        ordered_registry_slugs,
        persona_contract,
        team_default_member_slugs,
    )


MEETING_STATE_VERSION = "PATCH_29_MEETING_STATE_OBSERVABILITY_V1"


def _now_ts() -> int:
    return int(time.time())


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _clean_mode(value: Any) -> str:
    mode = _clean_text(value).lower()
    return mode if mode in {"team", "single", "multi"} else "team"


def _dedupe(values: Iterable[Any]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in values or []:
        text = _clean_text(item)
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out


def _profile_payload(slug: str) -> Optional[Dict[str, Any]]:
    canonical = canonical_agent_slug(slug, default="")
    if not canonical or canonical == "team":
        return None
    profile = CANONICAL_AGENT_REGISTRY.get(canonical)
    if not profile:
        return {
            "slug": canonical,
            "display_name": agent_display_name(canonical, default=canonical.title()),
            "role_label": "Agente",
            "present": True,
        }
    return {
        "slug": canonical,
        "display_name": getattr(profile, "display_name", canonical.title()),
        "role_label": getattr(profile, "role_label", "Agente"),
        "route_role": getattr(profile, "route_role", "specialist"),
        "internal": bool(getattr(profile, "internal", True)),
        "present": True,
    }


def _persona_payload(slug: Any) -> Dict[str, Any]:
    # PATCH_28_REV_A: persist persona identity explicitly alongside speaker.
    # The speaker can be recovered from active_speaker_slug, but the meeting
    # state must also carry the persona contract used for the active turn so
    # reconnect/reload/session recovery does not depend on implicit UI state.
    canonical = canonical_agent_slug(slug, default="")
    if canonical == "team":
        canonical = "orkio"
    if not canonical:
        canonical = "orkio"
    contract = persona_contract(canonical)
    return {
        "active_persona_slug": str(contract.get("slug") or canonical),
        "active_persona_scope": str(contract.get("persona_scope") or ""),
        "active_persona_guardrails": [
            str(rule)
            for rule in (contract.get("persona_guardrails") or [])
            if str(rule or "").strip()
        ],
        "persona_version": AGENT_REGISTRY_VERSION,
    }


def _transition_payload(
    *,
    previous_speaker_slug: Any = "",
    previous_speaker_name: Any = "",
    next_speaker_slug: Any = "",
    next_speaker_name: Any = "",
    previous_persona_slug: Any = "",
    next_persona_slug: Any = "",
    transition_reason: Any = "",
) -> Dict[str, Any]:
    # PATCH_29: persist compact transition metadata in last_turn so reconnect,
    # session recovery and external logs can explain why speaker/persona changed.
    prev_speaker = _clean_text(previous_speaker_slug)
    next_speaker = _clean_text(next_speaker_slug)
    prev_persona = _clean_text(previous_persona_slug)
    next_persona = _clean_text(next_persona_slug)
    return {
        "transition_reason": _clean_text(transition_reason) or "state_update",
        "speaker_transition": {
            "from_slug": prev_speaker,
            "from_name": _clean_text(previous_speaker_name),
            "to_slug": next_speaker,
            "to_name": _clean_text(next_speaker_name),
            "changed": bool(prev_speaker and next_speaker and prev_speaker != next_speaker),
        },
        "persona_transition": {
            "from_slug": prev_persona,
            "to_slug": next_persona,
            "changed": bool(prev_persona and next_persona and prev_persona != next_persona),
            "persona_version": AGENT_REGISTRY_VERSION,
        },
    }


def default_participant_slugs(*, include_internal: bool = True) -> List[str]:
    # PATCH_28: default meeting participants come from registry.team_default,
    # aligning Meeting State with the Team Panel router.
    slugs = []
    for slug in team_default_member_slugs(include_internal=include_internal):
        canonical = canonical_agent_slug(slug, default="")
        if canonical and canonical != "team":
            slugs.append(canonical)
    if not slugs:
        for slug in ordered_registry_slugs(include_internal=include_internal):
            canonical = canonical_agent_slug(slug, default="")
            if canonical and canonical != "team":
                slugs.append(canonical)
    if "orkio" not in slugs:
        slugs.insert(0, "orkio")
    return _dedupe(slugs)


def build_participants(
    participant_slugs: Optional[Iterable[Any]] = None,
    *,
    include_internal: bool = True,
) -> List[Dict[str, Any]]:
    slugs = list(participant_slugs or default_participant_slugs(include_internal=include_internal))
    items: List[Dict[str, Any]] = []
    for slug in _dedupe(slugs):
        payload = _profile_payload(slug)
        if payload:
            items.append(payload)
    return items


def _speaker_name(slug: Any, fallback: Any = "") -> str:
    canonical = canonical_agent_slug(slug, default="")
    if canonical:
        return agent_display_name(canonical, default=_clean_text(fallback) or canonical.title())
    return _clean_text(fallback)


def normalize_meeting_state(
    raw: Optional[Dict[str, Any]],
    *,
    session_id: Any = None,
    thread_id: Any = None,
    org: Any = None,
    user_id: Any = None,
    dest_mode: Any = None,
    include_internal: bool = True,
    now_ts: Optional[int] = None,
) -> Dict[str, Any]:
    now_value = int(now_ts or _now_ts())
    source = raw if isinstance(raw, dict) else {}

    participant_slugs = source.get("participant_slugs")
    if not isinstance(participant_slugs, list):
        participant_slugs = [
            item.get("slug")
            for item in (source.get("participants") or [])
            if isinstance(item, dict) and item.get("slug")
        ]
    participant_slugs = _dedupe(participant_slugs or default_participant_slugs(include_internal=include_internal))
    participants = build_participants(participant_slugs, include_internal=include_internal)

    active_slug = canonical_agent_slug(
        source.get("active_speaker_slug")
        or source.get("active_agent_slug")
        or source.get("target_agent_slug")
        or source.get("speaker_slug")
        or "",
        default="",
    )
    if active_slug == "team":
        active_slug = "orkio"
    if not active_slug:
        active_slug = "orkio"

    if active_slug not in participant_slugs and active_slug != "team":
        participant_slugs = _dedupe([active_slug] + participant_slugs)
        participants = build_participants(participant_slugs, include_internal=include_internal)

    last_slug = canonical_agent_slug(
        source.get("last_speaker_slug")
        or source.get("previous_speaker_slug")
        or "",
        default="",
    )

    return {
        "version": MEETING_STATE_VERSION,
        "session_id": _clean_text(session_id) or _clean_text(source.get("session_id")),
        "thread_id": _clean_text(thread_id) or _clean_text(source.get("thread_id")),
        "org": _clean_text(org) or _clean_text(source.get("org")),
        "user_id": _clean_text(user_id) or _clean_text(source.get("user_id")) or None,
        "mode": _clean_mode(dest_mode or source.get("mode") or source.get("dest_mode") or "team"),
        "room_mode": True,
        "participants": participants,
        "participant_slugs": participant_slugs,
        "active_speaker_slug": active_slug,
        "active_speaker_name": _speaker_name(active_slug, source.get("active_speaker_name")),
        **_persona_payload(active_slug),
        "last_speaker_slug": last_slug,
        "last_speaker_name": _speaker_name(last_slug, source.get("last_speaker_name")) if last_slug else "",
        "turn_index": int(source.get("turn_index") or 0),
        "history_loaded": bool(source.get("history_loaded", True)),
        "last_turn": source.get("last_turn") if isinstance(source.get("last_turn"), dict) else {},
        "started_at": int(source.get("started_at") or now_value),
        "updated_at": now_value,
    }


def build_initial_meeting_state(
    *,
    session_id: Any,
    thread_id: Any = None,
    org: Any = None,
    user_id: Any = None,
    dest_mode: Any = "team",
    active_agent_slug: Any = None,
    active_agent_name: Any = None,
    participant_slugs: Optional[Iterable[Any]] = None,
    include_internal: bool = True,
    history_loaded: bool = True,
    now_ts: Optional[int] = None,
) -> Dict[str, Any]:
    active_slug = canonical_agent_slug(active_agent_slug or active_agent_name or "orkio", default="orkio")
    raw = {
        "session_id": session_id,
        "thread_id": thread_id,
        "org": org,
        "user_id": user_id,
        "mode": dest_mode,
        "participant_slugs": list(participant_slugs or default_participant_slugs(include_internal=include_internal)),
        "active_speaker_slug": active_slug if active_slug != "team" else "orkio",
        "active_speaker_name": active_agent_name or _speaker_name(active_slug),
        "turn_index": 0,
        "history_loaded": bool(history_loaded),
        "last_turn": {
            "kind": "session_start",
            "source": "realtime_start",
            "target_agent_slug": active_slug if active_slug != "team" else "orkio",
            "transition_reason": "session_start",
            "speaker_transition": {
                "from_slug": "",
                "from_name": "",
                "to_slug": active_slug if active_slug != "team" else "orkio",
                "to_name": active_agent_name or _speaker_name(active_slug),
                "changed": False,
            },
            "persona_transition": {
                "from_slug": "",
                "to_slug": active_slug if active_slug != "team" else "orkio",
                "changed": False,
                "persona_version": AGENT_REGISTRY_VERSION,
            },
        },
    }
    return normalize_meeting_state(
        raw,
        session_id=session_id,
        thread_id=thread_id,
        org=org,
        user_id=user_id,
        dest_mode=dest_mode,
        include_internal=include_internal,
        now_ts=now_ts,
    )


def apply_turn_to_meeting_state(
    state: Optional[Dict[str, Any]],
    *,
    session_id: Any = None,
    thread_id: Any = None,
    org: Any = None,
    user_id: Any = None,
    dest_mode: Any = None,
    target_agent_slug: Any = None,
    target_agent_name: Any = None,
    target_agent_slugs: Optional[Iterable[Any]] = None,
    multi_agent_turn: Any = False,
    response_control: Any = None,
    kind: Any = "turn",
    source: Any = "runtime",
    confidence: Any = None,
    transcript: Any = None,
    include_internal: bool = True,
    now_ts: Optional[int] = None,
) -> Dict[str, Any]:
    current = normalize_meeting_state(
        state,
        session_id=session_id,
        thread_id=thread_id,
        org=org,
        user_id=user_id,
        dest_mode=dest_mode,
        include_internal=include_internal,
        now_ts=now_ts,
    )

    target_slug = canonical_agent_slug(target_agent_slug or target_agent_name or "", default="")
    if target_slug == "team":
        target_slug = "orkio"

    sequence_slugs = [
        canonical_agent_slug(slug, default="")
        for slug in (target_agent_slugs or [])
        if canonical_agent_slug(slug, default="")
    ]
    sequence_slugs = _dedupe([slug for slug in sequence_slugs if slug != "team"])
    if target_slug and target_slug not in sequence_slugs:
        sequence_slugs = _dedupe([target_slug] + sequence_slugs)

    for slug in sequence_slugs:
        if slug and slug not in list(current.get("participant_slugs") or []):
            current["participant_slugs"] = _dedupe(list(current.get("participant_slugs") or []) + [slug])
            current["participants"] = build_participants(current["participant_slugs"], include_internal=include_internal)

    prev_slug = current.get("active_speaker_slug") or ""
    prev_name = current.get("active_speaker_name") or ""
    prev_persona_slug = current.get("active_persona_slug") or ""
    transition_reason = _clean_text(kind) or "turn"

    if target_slug:
        if target_slug != prev_slug:
            current["last_speaker_slug"] = prev_slug
            current["last_speaker_name"] = prev_name
        current["active_speaker_slug"] = target_slug
        current["active_speaker_name"] = _speaker_name(target_slug, target_agent_name)
        current.update(_persona_payload(target_slug))
        if target_slug not in list(current.get("participant_slugs") or []):
            current["participant_slugs"] = _dedupe([target_slug] + list(current.get("participant_slugs") or []))
            current["participants"] = build_participants(current["participant_slugs"], include_internal=include_internal)

    current["mode"] = _clean_mode(dest_mode or current.get("mode") or "team")
    current["turn_index"] = int(current.get("turn_index") or 0) + 1
    current["updated_at"] = int(now_ts or _now_ts())
    transition = _transition_payload(
        previous_speaker_slug=prev_slug,
        previous_speaker_name=prev_name,
        next_speaker_slug=current.get("active_speaker_slug") or "",
        next_speaker_name=current.get("active_speaker_name") or "",
        previous_persona_slug=prev_persona_slug,
        next_persona_slug=current.get("active_persona_slug") or "",
        transition_reason=transition_reason,
    )
    current["last_turn"] = {
        "kind": _clean_text(kind) or "turn",
        "source": _clean_text(source) or "runtime",
        "target_agent_slug": current.get("active_speaker_slug") or "",
        "target_agent_name": current.get("active_speaker_name") or "",
        "active_persona_slug": current.get("active_persona_slug") or "",
        "persona_version": current.get("persona_version") or AGENT_REGISTRY_VERSION,
        "confidence": confidence,
        "transcript_preview": _clean_text(transcript)[:240],
        "target_agent_slugs": sequence_slugs,
        "multi_agent_turn": bool(multi_agent_turn or len(sequence_slugs) > 1),
        "response_control": _clean_text(response_control) or ("sequenced_team_turns" if len(sequence_slugs) > 1 else "single_turn"),
        **transition,
    }
    current["target_agent_slugs"] = sequence_slugs
    current["multi_agent_turn"] = bool(multi_agent_turn or len(sequence_slugs) > 1)
    current["response_control"] = current["last_turn"]["response_control"]
    if len(sequence_slugs) > 1:
        current["sequence_remaining"] = sequence_slugs[1:]
    else:
        current["sequence_remaining"] = []
    return current


def update_meeting_state_from_directive(
    state: Optional[Dict[str, Any]],
    directive: Optional[Dict[str, Any]],
    *,
    session_id: Any = None,
    thread_id: Any = None,
    org: Any = None,
    user_id: Any = None,
    dest_mode: Any = None,
    include_internal: bool = True,
    now_ts: Optional[int] = None,
) -> Dict[str, Any]:
    directive = directive if isinstance(directive, dict) else {}
    target = directive.get("target_agent") if isinstance(directive.get("target_agent"), dict) else {}
    return apply_turn_to_meeting_state(
        state,
        session_id=session_id or directive.get("session_id"),
        thread_id=thread_id,
        org=org,
        user_id=user_id,
        dest_mode=dest_mode,
        target_agent_slug=directive.get("target_agent_slug") or target.get("slug") or target.get("display_name"),
        target_agent_name=target.get("display_name") or directive.get("visible_agent"),
        target_agent_slugs=directive.get("target_agent_slugs") or [],
        multi_agent_turn=bool(directive.get("multi_agent_turn")),
        response_control=directive.get("response_control"),
        kind=directive.get("kind") or directive.get("match_type") or "directive",
        source="meeting_orchestrator",
        confidence=directive.get("confidence"),
        transcript=directive.get("transcript"),
        include_internal=include_internal,
        now_ts=now_ts,
    )


def meeting_state_from_meta(meta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    meta = meta if isinstance(meta, dict) else {}
    state = meta.get("meeting_state")
    return state if isinstance(state, dict) else {}


def merge_meeting_state_into_meta(meta: Optional[Dict[str, Any]], state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    out = dict(meta or {})
    if isinstance(state, dict) and state:
        out["meeting_state"] = state
        out["meeting_state_version"] = state.get("version") or MEETING_STATE_VERSION
    return out


def summarize_meeting_state_for_log(state: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    state = state if isinstance(state, dict) else {}
    return {
        "version": state.get("version") or MEETING_STATE_VERSION,
        "session_id": state.get("session_id") or "",
        "mode": state.get("mode") or "",
        "active_speaker_slug": state.get("active_speaker_slug") or "",
        "active_speaker_name": state.get("active_speaker_name") or "",
        "active_persona_slug": state.get("active_persona_slug") or "",
        "persona_version": state.get("persona_version") or "",
        "last_speaker_slug": state.get("last_speaker_slug") or "",
        "turn_index": state.get("turn_index") or 0,
        "participants": list(state.get("participants") or state.get("participant_slugs") or state.get("target_agent_slugs") or []),
        "multi_agent_turn": bool(state.get("multi_agent_turn")),
        "response_control": state.get("response_control") or "",
        "target_agent_slugs": list(state.get("target_agent_slugs") or []),
        "transition_reason": (state.get("last_turn") or {}).get("transition_reason") if isinstance(state.get("last_turn"), dict) else "",
        "speaker_transition": (state.get("last_turn") or {}).get("speaker_transition") if isinstance(state.get("last_turn"), dict) else {},
        "persona_transition": (state.get("last_turn") or {}).get("persona_transition") if isinstance(state.get("last_turn"), dict) else {},
    }


__all__ = [
    "MEETING_STATE_VERSION",
    "apply_turn_to_meeting_state",
    "build_initial_meeting_state",
    "build_participants",
    "default_participant_slugs",
    "meeting_state_from_meta",
    "merge_meeting_state_into_meta",
    "normalize_meeting_state",
    "summarize_meeting_state_for_log",
    "update_meeting_state_from_directive",
]
