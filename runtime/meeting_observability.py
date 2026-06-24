# PATCH_29_OBSERVABILIDADE_E_LOGS
# Dependency-free observability helpers for the Patroai realtime meeting room.
#
# Purpose:
# - Emit deterministic transition summaries without migrations.
# - Make speaker/persona transitions auditable after Direct Addressing,
#   Turn Router, Meeting State, Multi-Agent and Persona Isolation patches.
# - Keep logs JSON-safe and fail-open.

from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterable, List, Optional

try:  # Runtime package import
    from app.runtime.agent_registry import AGENT_REGISTRY_VERSION
except Exception:  # pragma: no cover - local package fallback for tests
    try:
        from .agent_registry import AGENT_REGISTRY_VERSION
    except Exception:  # pragma: no cover
        AGENT_REGISTRY_VERSION = "unknown"

try:  # Runtime package import
    from app.runtime.meeting_state import MEETING_STATE_VERSION
except Exception:  # pragma: no cover - local package fallback for tests
    try:
        from .meeting_state import MEETING_STATE_VERSION
    except Exception:  # pragma: no cover
        MEETING_STATE_VERSION = "unknown"


MEETING_OBSERVABILITY_VERSION = "PATCH_29_MEETING_OBSERVABILITY_V1"


def _now_ts() -> int:
    return int(time.time())


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _safe_list(values: Any) -> List[str]:
    if not isinstance(values, (list, tuple, set)):
        return []
    out: List[str] = []
    seen = set()
    for item in values:
        text = _clean(item)
        if not text:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
    return out


def _safe_bool(value: Any) -> bool:
    return bool(value)


def _safe_confidence(value: Any) -> Optional[float]:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _route_reason(directive: Dict[str, Any], next_state: Dict[str, Any]) -> str:
    for key in ("transition_reason", "route_reason", "kind", "match_type"):
        text = _clean(directive.get(key))
        if text:
            return text
    last_turn = _dict(next_state.get("last_turn"))
    for key in ("transition_reason", "kind", "source"):
        text = _clean(last_turn.get(key))
        if text:
            return text
    return "state_update"


def _speaker_transition(previous_state: Dict[str, Any], next_state: Dict[str, Any]) -> Dict[str, Any]:
    from_slug = _clean(previous_state.get("active_speaker_slug"))
    to_slug = _clean(next_state.get("active_speaker_slug"))
    return {
        "from_slug": from_slug,
        "from_name": _clean(previous_state.get("active_speaker_name")),
        "to_slug": to_slug,
        "to_name": _clean(next_state.get("active_speaker_name")),
        "changed": from_slug != to_slug,
    }


def _persona_transition(previous_state: Dict[str, Any], next_state: Dict[str, Any]) -> Dict[str, Any]:
    from_slug = _clean(previous_state.get("active_persona_slug"))
    to_slug = _clean(next_state.get("active_persona_slug"))
    from_scope = _clean(previous_state.get("active_persona_scope"))
    to_scope = _clean(next_state.get("active_persona_scope"))
    previous_rules = _safe_list(previous_state.get("active_persona_guardrails"))
    next_rules = _safe_list(next_state.get("active_persona_guardrails"))
    return {
        "from_slug": from_slug,
        "to_slug": to_slug,
        "changed": from_slug != to_slug,
        "scope_changed": bool(from_scope and to_scope and from_scope != to_scope),
        "guardrails_changed": bool(previous_rules and next_rules and previous_rules != next_rules),
        "persona_version": _clean(next_state.get("persona_version") or previous_state.get("persona_version") or AGENT_REGISTRY_VERSION),
    }


def _route_payload(directive: Dict[str, Any], next_state: Dict[str, Any]) -> Dict[str, Any]:
    turn_router = _dict(directive.get("turn_router"))
    last_turn = _dict(next_state.get("last_turn"))
    target_agent_slugs = (
        directive.get("target_agent_slugs")
        or turn_router.get("target_agent_slugs")
        or next_state.get("target_agent_slugs")
        or last_turn.get("target_agent_slugs")
        or []
    )
    confidence = (
        _safe_confidence(directive.get("confidence"))
        if directive.get("confidence") is not None
        else _safe_confidence(turn_router.get("confidence") if turn_router else last_turn.get("confidence"))
    )
    return {
        "kind": _clean(directive.get("kind") or last_turn.get("kind")),
        "match_type": _clean(directive.get("match_type") or turn_router.get("match_type") or last_turn.get("kind")),
        "transition_reason": _route_reason(directive, next_state),
        "target_agent_slug": _clean(directive.get("target_agent_slug") or next_state.get("active_speaker_slug")),
        "target_agent_slugs": _safe_list(target_agent_slugs),
        "multi_agent_turn": _safe_bool(directive.get("multi_agent_turn") or next_state.get("multi_agent_turn")),
        "response_control": _clean(directive.get("response_control") or next_state.get("response_control") or last_turn.get("response_control")),
        "confidence": confidence,
        "dedupe_key": _clean(directive.get("dedupe_key")),
    }


def build_meeting_transition_log(
    *,
    previous_state: Optional[Dict[str, Any]],
    next_state: Optional[Dict[str, Any]],
    directive: Optional[Dict[str, Any]] = None,
    source: Any = "runtime",
    persisted: Any = None,
    now_ts: Optional[int] = None,
) -> Dict[str, Any]:
    """Build a JSON-safe transition log for meeting state changes.

    This helper intentionally does not write to a database or logging backend.
    Routes may log the returned dict and/or include a compact summary in the
    API response. It is safe to call even when directive/state is missing.
    """
    prev = _dict(previous_state)
    nxt = _dict(next_state)
    d = _dict(directive)
    route = _route_payload(d, nxt)
    speaker_transition = _speaker_transition(prev, nxt)
    persona_transition = _persona_transition(prev, nxt)

    transition_reason = route.get("transition_reason") or _route_reason(d, nxt)
    event = {
        "event": "meeting_transition",
        "observability_version": MEETING_OBSERVABILITY_VERSION,
        "timestamp": int(now_ts or _now_ts()),
        "source": _clean(source) or "runtime",
        "session_id": _clean(nxt.get("session_id") or d.get("session_id") or prev.get("session_id")),
        "thread_id": _clean(nxt.get("thread_id") or d.get("thread_id") or prev.get("thread_id")),
        "meeting_state_version": _clean(nxt.get("version") or MEETING_STATE_VERSION),
        "agent_registry_version": _clean(d.get("agent_registry_version") or nxt.get("persona_version") or AGENT_REGISTRY_VERSION),
        "turn_router_version": _clean(d.get("turn_router_version")),
        "turn_index": int(nxt.get("turn_index") or 0),
        "room_mode": bool(nxt.get("room_mode", True)),
        "transition_reason": transition_reason,
        "speaker_transition": speaker_transition,
        "persona_transition": persona_transition,
        "route": route,
        "participants": _safe_list(nxt.get("participant_slugs")),
        "persisted": persisted if persisted is None else bool(persisted),
    }

    # Flatten the most important fields for easy grep and metric extraction.
    event["speaker_from"] = speaker_transition.get("from_slug") or ""
    event["speaker_to"] = speaker_transition.get("to_slug") or ""
    event["persona_from"] = persona_transition.get("from_slug") or ""
    event["persona_to"] = persona_transition.get("to_slug") or ""
    event["persona_version"] = persona_transition.get("persona_version") or ""
    return event


def summarize_transition_for_response(event: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    event = _dict(event)
    route = _dict(event.get("route"))
    speaker = _dict(event.get("speaker_transition"))
    persona = _dict(event.get("persona_transition"))
    return {
        "observability_version": event.get("observability_version") or MEETING_OBSERVABILITY_VERSION,
        "transition_reason": event.get("transition_reason") or route.get("transition_reason") or "",
        "speaker_transition": {
            "from_slug": speaker.get("from_slug") or "",
            "to_slug": speaker.get("to_slug") or "",
            "changed": bool(speaker.get("changed")),
        },
        "persona_transition": {
            "from_slug": persona.get("from_slug") or "",
            "to_slug": persona.get("to_slug") or "",
            "changed": bool(persona.get("changed")),
            "persona_version": persona.get("persona_version") or event.get("persona_version") or "",
        },
        "route": {
            "kind": route.get("kind") or "",
            "match_type": route.get("match_type") or "",
            "target_agent_slug": route.get("target_agent_slug") or "",
            "target_agent_slugs": _safe_list(route.get("target_agent_slugs")),
            "multi_agent_turn": bool(route.get("multi_agent_turn")),
            "response_control": route.get("response_control") or "",
        },
        "turn_index": event.get("turn_index") or 0,
        "persisted": event.get("persisted"),
    }


def transition_log_line(event: Optional[Dict[str, Any]]) -> str:
    """Return compact deterministic JSON for logger.warning/info."""
    try:
        return json.dumps(_dict(event), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except Exception:
        return "{}"


__all__ = [
    "MEETING_OBSERVABILITY_VERSION",
    "build_meeting_transition_log",
    "summarize_transition_for_response",
    "transition_log_line",
]
