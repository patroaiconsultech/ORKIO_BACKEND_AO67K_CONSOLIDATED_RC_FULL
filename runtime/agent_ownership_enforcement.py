"""OEC-004 — immutable agent ownership enforcement.

Pure helpers used by chat persistence, legacy continuity fast-paths and the
final SSE response envelope. No database or network side effects.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

OEC004_OWNERSHIP_ENFORCEMENT_VERSION = "OEC004_IMMUTABLE_AGENT_OWNERSHIP_V1"

_AGENT_DISPLAY = {
    "orkio": ("orkio", "Orkio"),
    "orion": ("orion", "Orion"),
    "chris": ("chris", "Chris"),
    "laura": ("laura", "Laura"),
    "team": ("team", "Team"),
}


def _norm(value: Any) -> str:
    raw = str(value or "").strip().lower().lstrip("@")
    if raw == "cris":
        return "chris"
    return raw


def _locked_owner(turn_context: Any) -> Optional[Tuple[str, str]]:
    if turn_context is None or not bool(getattr(turn_context, "ownership_locked", False)):
        return None

    requested = _norm(getattr(turn_context, "requested_agent", None))
    owner = _norm(getattr(turn_context, "turn_owner", None))
    display = _norm(getattr(turn_context, "display_agent", None))
    canonical = requested or owner or display
    if canonical not in _AGENT_DISPLAY:
        return None
    return _AGENT_DISPLAY[canonical]


def should_allow_chris_context_continuity(turn_context: Any) -> Tuple[bool, str]:
    """Chris may own a turn only when ownership is unlocked or explicitly Chris."""
    locked = _locked_owner(turn_context)
    if locked is None:
        return True, "ownership_unlocked"
    agent_id, _ = locked
    if agent_id == "chris":
        return True, "explicit_chris_owner"
    return False, "explicit_non_chris_owner"


def resolve_persistence_owner(
    agent_id: Optional[str],
    agent_name: Optional[str],
    turn_context: Any,
) -> Tuple[Optional[str], str, bool]:
    """Return canonical persistence identity for a locked explicit owner."""
    locked = _locked_owner(turn_context)
    current_name = str(agent_name or "Orkio").strip() or "Orkio"
    if locked is None:
        return agent_id, current_name, False

    locked_id, locked_name = locked
    changed = _norm(agent_id) != locked_id or current_name != locked_name
    return locked_id, locked_name, changed


def enforce_locked_payload_owner(
    payload: Optional[Dict[str, Any]],
    turn_context: Any,
) -> Tuple[Dict[str, Any], bool]:
    """Normalize final response identity without changing content or permissions."""
    out: Dict[str, Any] = dict(payload or {})
    locked = _locked_owner(turn_context)
    if locked is None:
        return out, False

    locked_id, locked_name = locked
    before = (
        _norm(out.get("agent_id")),
        str(out.get("agent_name") or "").strip(),
        str(out.get("final_speaker") or "").strip(),
    )

    out["agent_id"] = locked_id
    out["agent_name"] = locked_name
    out["final_speaker"] = locked_name
    out["visible_agent"] = locked_name
    out["speaker_name"] = locked_name

    runtime_hints = out.get("runtime_hints")
    runtime_hints = dict(runtime_hints) if isinstance(runtime_hints, dict) else {}
    routing = runtime_hints.get("routing")
    routing = dict(routing) if isinstance(routing, dict) else {}
    routing.update({
        "requested_agent": getattr(turn_context, "requested_agent", locked_id),
        "turn_owner": getattr(turn_context, "turn_owner", locked_id),
        "display_agent": getattr(turn_context, "display_agent", locked_id),
        "ownership_locked": True,
        "ownership_enforcement_version": OEC004_OWNERSHIP_ENFORCEMENT_VERSION,
    })
    runtime_hints["routing"] = routing
    out["runtime_hints"] = runtime_hints

    after = (locked_id, locked_name, locked_name)
    return out, before != after
