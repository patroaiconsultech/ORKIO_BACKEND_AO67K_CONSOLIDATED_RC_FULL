"""
PATCH 34 REV B — Realtime Room Engine Full Integration

New backend module suggested path:
    runtime/realtime_room_engine.py

Operational goal:
    Keep Team as a persistent runtime room and switch speakers inside the room
    without allowing legacy manual_agent_authority_single events to collapse the
    room back to single mode.

No external dependencies. Python 3.10+ recommended.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Tuple
import copy
import json
import logging
import re
import uuid


PATCH34_ROOM_ENGINE_VERSION = "PATCH_34_REVB_REALTIME_ROOM_ENGINE_FULL_INTEGRATION_V1"
PATCH34_ROOM_ENGINE_REVA_COMPAT_VERSION = "PATCH_34_REVA_REALTIME_ROOM_ENGINE_V1"
PATCH34_ROOM_RESPONSE_CONTROL = "room_agent_authority"
PATCH34_ROOM_MODE = "team"

CANONICAL_TEAM_PARTICIPANTS = ("orkio", "orion", "chris", "laura")
VALID_AGENT_SLUGS = set(CANONICAL_TEAM_PARTICIPANTS)
TEAM_SLUG_ALIASES = {"team", "all", "sala", "sala_team", "room", "overview"}


class RoomMode(str, Enum):
    SINGLE = "single"
    TEAM = "team"


class RoomPhase(str, Enum):
    IDLE = "IDLE"
    SPEAKING = "SPEAKING"
    SWITCH_PENDING = "SWITCH_PENDING"
    SWITCHING = "SWITCHING"
    READY = "READY"
    ENDED = "ENDED"


@dataclass
class RoomState:
    org: str = "public"
    room_id: str = ""
    session_id: str = ""
    thread_id: str = ""

    room_mode: str = RoomMode.TEAM.value
    participants: List[str] = field(default_factory=lambda: list(CANONICAL_TEAM_PARTICIPANTS))

    active_speaker_slug: str = "orkio"
    active_persona_slug: str = "orkio"
    active_speaker_name: str = "Orkio"
    pending_speaker_slug: str = ""
    last_speaker_slug: str = ""

    target_agent_slug: str = "orkio"
    target_agent_slugs: List[str] = field(default_factory=lambda: list(CANONICAL_TEAM_PARTICIPANTS))
    multi_agent_turn: bool = True
    response_control: str = "room_agent_authority"

    phase: str = RoomPhase.IDLE.value
    turn_index: int = 0
    transition_reason: str = "room_state_created"
    last_event_name: str = ""
    last_dedupe_key: str = ""

    has_snapshot: bool = True
    persisted: bool = True
    realtime_session_active: bool = True
    stale_payloads_ignored: int = 0
    empty_state_ignored: int = 0
    team_collapse_blocked: int = 0

    version: str = PATCH34_ROOM_ENGINE_VERSION
    created_at: str = ""
    updated_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["state"] = self.phase  # compatibility with existing frontend naming
        payload["mode"] = self.room_mode  # compatibility with PATCH_29/PATCH_32 meeting_state
        return payload


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_slug(value: Any, default: str = "") -> str:
    if value is None:
        return default
    slug = str(value).strip().lower()
    slug = re.sub(r"[^a-z0-9_-]+", "_", slug)
    if slug in {"", "none", "null", "undefined"}:
        return default
    if slug in {"laura_pat" , "laura_patroai"}:
        return "laura"
    return slug


def display_name_for_slug(slug: str) -> str:
    return {
        "orkio": "Orkio",
        "orion": "Orion",
        "chris": "Chris",
        "laura": "Laura",
        "team": "Team",
    }.get(slug, slug.capitalize() if slug else "")


def unique_valid_participants(values: Optional[Iterable[Any]]) -> List[str]:
    result: List[str] = []
    for raw in values or []:
        slug = normalize_slug(raw)
        if slug in VALID_AGENT_SLUGS and slug not in result:
            result.append(slug)
    return result or list(CANONICAL_TEAM_PARTICIPANTS)


def deep_get(data: Mapping[str, Any], *path: str, default: Any = None) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, Mapping) or key not in cur:
            return default
        cur = cur[key]
    return cur


def extract_event_name(event: Mapping[str, Any]) -> str:
    return str(
        event.get("name")
        or event.get("event")
        or event.get("type")
        or deep_get(event, "payload", "name", default="")
        or ""
    )


def extract_session_id(event: Mapping[str, Any], fallback: str = "") -> str:
    return str(
        event.get("session_id")
        or deep_get(event, "payload", "session_id", default="")
        or deep_get(event, "meeting_state", "session_id", default="")
        or fallback
        or ""
    )


def extract_thread_id(event: Mapping[str, Any], fallback: str = "") -> str:
    return str(
        event.get("thread_id")
        or deep_get(event, "payload", "thread_id", default="")
        or deep_get(event, "meeting_state", "thread_id", default="")
        or fallback
        or ""
    )


def extract_target_slug(event: Mapping[str, Any]) -> str:
    candidates = [
        event.get("target"),
        event.get("target_slug"),
        event.get("target_agent_slug"),
        event.get("manual_target_slug"),
        deep_get(event, "payload", "target", default=None),
        deep_get(event, "payload", "target_slug", default=None),
        deep_get(event, "payload", "target_agent_slug", default=None),
        deep_get(event, "payload", "manual_target_slug", default=None),
        deep_get(event, "route", "target_agent_slug", default=None),
        deep_get(event, "payload", "route", "target_agent_slug", default=None),
    ]
    for candidate in candidates:
        slug = normalize_slug(candidate)
        if slug:
            return slug

    targets = (
        event.get("targets")
        or event.get("target_agent_slugs")
        or deep_get(event, "payload", "targets", default=None)
        or deep_get(event, "payload", "target_agent_slugs", default=None)
        or deep_get(event, "route", "target_agent_slugs", default=None)
        or []
    )
    if isinstance(targets, (list, tuple)) and targets:
        normalized = [normalize_slug(item) for item in targets]
        normalized = [item for item in normalized if item]
        if set(normalized).issuperset(VALID_AGENT_SLUGS):
            return "team"
        return normalized[0]
    return ""


def incoming_state_is_empty_or_destructive(incoming: Mapping[str, Any]) -> bool:
    if not incoming:
        return True

    active = normalize_slug(incoming.get("active_speaker_slug") or incoming.get("active_persona_slug"))
    targets = incoming.get("target_agent_slugs") or []
    session_id = incoming.get("session_id") or ""

    destructive_empty = (
        not active
        and not targets
        and not session_id
        and incoming.get("participants") in (None, [], "")
    )
    return destructive_empty


def incoming_would_collapse_team(incoming: Mapping[str, Any]) -> bool:
    mode = normalize_slug(incoming.get("mode") or incoming.get("room_mode"))
    response_control = str(incoming.get("response_control") or "")
    multi_agent_turn = incoming.get("multi_agent_turn")
    targets = incoming.get("target_agent_slugs") or []

    return (
        mode == "single"
        or multi_agent_turn is False
        or response_control == "manual_agent_authority_single"
        or (isinstance(targets, list) and len(targets) == 1)
    )


class RealtimeRoomEngine:
    """
    Small deterministic room-state engine.

    Persistence hook:
        persist_hook(state_dict) -> bool

    The hook can write to Redis/DB existing storage. If no hook is supplied,
    the in-memory snapshot is still marked persisted=True for runtime safety,
    but production should wire a durable hook.
    """

    def __init__(
        self,
        *,
        persist_hook: Optional[Callable[[Dict[str, Any]], bool]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._rooms: Dict[str, RoomState] = {}
        self._persist_hook = persist_hook
        self._log = logger or logging.getLogger("orkio.realtime.room_engine")

    def _key(self, org: str, session_id: str) -> str:
        return f"{org or 'public'}:{session_id}"

    def _persist(self, state: RoomState) -> bool:
        state.updated_at = utc_now_iso()
        state.has_snapshot = True

        if self._persist_hook is None:
            state.persisted = True
            return True

        try:
            ok = bool(self._persist_hook(state.to_dict()))
            state.persisted = ok
            return ok
        except Exception as exc:  # defensive: do not break realtime due to logging/storage
            state.persisted = False
            state.metadata["persist_error"] = repr(exc)
            self._log.exception("PATCH34_REVB_ROOM_PERSIST_FAILED session_id=%s", state.session_id)
            return False

    def get(self, session_id: str, *, org: str = "public") -> Optional[RoomState]:
        return self._rooms.get(self._key(org, session_id))

    def get_snapshot(self, session_id: str, *, org: str = "public") -> Optional[Dict[str, Any]]:
        state = self.get(session_id, org=org)
        if not state:
            return None
        self._log.error(
            "PATCH34_REVB_SESSION_SNAPSHOT_AVAILABLE org=%s session_id=%s has_snapshot=%s persisted=%s room_mode=%s active_speaker_slug=%s phase=%s",
            org,
            session_id,
            state.has_snapshot,
            state.persisted,
            state.room_mode,
            state.active_speaker_slug,
            state.phase,
        )
        return copy.deepcopy(state.to_dict())

    def ensure_room(
        self,
        *,
        session_id: str,
        org: str = "public",
        thread_id: str = "",
        room_mode: str = "team",
        participants: Optional[Iterable[Any]] = None,
        active_speaker_slug: str = "orkio",
        reason: str = "ensure_room",
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> RoomState:
        session_id = str(session_id or "").strip()
        if not session_id:
            raise ValueError("PATCH34 room_state requires session_id")

        key = self._key(org, session_id)
        existing = self._rooms.get(key)
        participants_list = unique_valid_participants(participants)
        room_mode_norm = normalize_slug(room_mode, default="team")
        if room_mode_norm in TEAM_SLUG_ALIASES:
            room_mode_norm = RoomMode.TEAM.value
        if room_mode_norm not in {RoomMode.TEAM.value, RoomMode.SINGLE.value}:
            room_mode_norm = RoomMode.TEAM.value

        active = normalize_slug(active_speaker_slug, default="orkio")
        if active not in VALID_AGENT_SLUGS:
            active = "orkio"

        if existing:
            if thread_id and not existing.thread_id:
                existing.thread_id = thread_id
            if room_mode_norm == RoomMode.TEAM.value:
                existing.room_mode = RoomMode.TEAM.value
                existing.participants = participants_list
                existing.target_agent_slugs = participants_list
                existing.multi_agent_turn = True
                existing.response_control = "room_agent_authority"
            existing.transition_reason = reason
            if metadata:
                existing.metadata.update(dict(metadata))
            self._persist(existing)
            return existing

        now = utc_now_iso()
        room_id = f"room_{uuid.uuid4().hex[:16]}"
        if room_mode_norm == RoomMode.TEAM.value:
            target_agent_slugs = participants_list
            multi_agent_turn = True
            response_control = "room_agent_authority"
        else:
            target_agent_slugs = [active]
            multi_agent_turn = False
            response_control = "manual_agent_authority_single"

        state = RoomState(
            org=org or "public",
            room_id=room_id,
            session_id=session_id,
            thread_id=thread_id or "",
            room_mode=room_mode_norm,
            participants=participants_list,
            active_speaker_slug=active,
            active_persona_slug=active,
            active_speaker_name=display_name_for_slug(active),
            target_agent_slug=active,
            target_agent_slugs=target_agent_slugs,
            multi_agent_turn=multi_agent_turn,
            response_control=response_control,
            phase=RoomPhase.READY.value,
            transition_reason=reason,
            created_at=now,
            updated_at=now,
            metadata=dict(metadata or {}),
        )
        self._rooms[key] = state
        self._persist(state)
        self._log.error(
            "PATCH34_REVB_ROOM_STATE_CREATED org=%s session_id=%s room_id=%s room_mode=%s participants=%s active_speaker_slug=%s room_state_persisted=%s has_snapshot=%s version=%s",
            state.org,
            state.session_id,
            state.room_id,
            state.room_mode,
            json.dumps(state.participants, ensure_ascii=False),
            state.active_speaker_slug,
            state.persisted,
            state.has_snapshot,
            state.version,
        )
        return state

    def apply_manual_directive(
        self,
        event: Mapping[str, Any],
        *,
        org: str = "public",
        session_id: str = "",
        thread_id: str = "",
    ) -> Tuple[RoomState, Dict[str, Any]]:
        sid = extract_session_id(event, fallback=session_id)
        if not sid:
            raise ValueError("PATCH34 manual directive requires session_id")

        tid = extract_thread_id(event, fallback=thread_id)
        event_name = extract_event_name(event)
        target = extract_target_slug(event) or "orkio"
        target = "team" if target in TEAM_SLUG_ALIASES else target
        participants = unique_valid_participants(
            event.get("participants")
            or deep_get(event, "payload", "participants", default=None)
            or deep_get(event, "meeting_state", "participants", default=None)
            or CANONICAL_TEAM_PARTICIPANTS
        )

        wants_team = (
            target == "team"
            or normalize_slug(event.get("room_mode")) == "team"
            or deep_get(event, "payload", "room_mode", default="") == "team"
            or bool(event.get("room_mode") is True)
            or bool(deep_get(event, "payload", "room_mode", default=False) is True)
        )

        state = self.ensure_room(
            session_id=sid,
            org=org,
            thread_id=tid,
            room_mode=RoomMode.TEAM.value if wants_team else RoomMode.TEAM.value,  # safe default: keep Team alive
            participants=participants,
            active_speaker_slug="orkio" if target == "team" else target,
            reason="manual_agent_button",
            metadata={"patch34_event_name": event_name},
        )

        old = state.active_speaker_slug

        if target == "team":
            state.room_mode = RoomMode.TEAM.value
            state.participants = participants
            state.target_agent_slugs = participants
            state.multi_agent_turn = True
            state.response_control = "room_team_authority"
            state.pending_speaker_slug = ""
            state.active_speaker_slug = "orkio"
            state.active_persona_slug = "orkio"
            state.active_speaker_name = "Orkio"
            state.target_agent_slug = "orkio"
            state.phase = RoomPhase.READY.value
        elif target in VALID_AGENT_SLUGS:
            # Critical invariant: if the room is Team, selecting a single agent only changes the speaker.
            # It must not collapse room_mode to single.
            if state.room_mode == RoomMode.TEAM.value:
                state.last_speaker_slug = old
                state.pending_speaker_slug = target if target != old else ""
                state.active_speaker_slug = target
                state.active_persona_slug = target
                state.active_speaker_name = display_name_for_slug(target)
                state.target_agent_slug = target
                state.target_agent_slugs = participants
                state.multi_agent_turn = True
                state.response_control = "room_agent_authority"
                state.phase = RoomPhase.SWITCH_PENDING.value if target != old else RoomPhase.READY.value
            else:
                state.last_speaker_slug = old
                state.active_speaker_slug = target
                state.active_persona_slug = target
                state.active_speaker_name = display_name_for_slug(target)
                state.target_agent_slug = target
                state.target_agent_slugs = [target]
                state.multi_agent_turn = False
                state.response_control = "manual_agent_authority_single"
                state.phase = RoomPhase.SWITCH_PENDING.value if target != old else RoomPhase.READY.value
        else:
            state.metadata["ignored_invalid_target_slug"] = target

        state.turn_index += 1
        state.transition_reason = "manual_agent_button"
        state.last_event_name = event_name
        state.last_dedupe_key = str(
            event.get("dedupe_key")
            or deep_get(event, "payload", "dedupe_key", default="")
            or ""
        )

        self._persist(state)
        self._log.error(
            "PATCH34_REVB_ROOM_MANUAL_DIRECTIVE_APPLIED org=%s session_id=%s room_mode=%s target=%s active_speaker_slug=%s pending_speaker_slug=%s target_agent_slugs=%s multi_agent_turn=%s response_control=%s room_state_persisted=%s has_snapshot=%s version=%s",
            state.org,
            state.session_id,
            state.room_mode,
            target,
            state.active_speaker_slug,
            state.pending_speaker_slug,
            json.dumps(state.target_agent_slugs, ensure_ascii=False),
            state.multi_agent_turn,
            state.response_control,
            state.persisted,
            state.has_snapshot,
            state.version,
        )

        return state, state.to_dict()

    def merge_incoming_meeting_state(
        self,
        *,
        session_id: str,
        incoming: Optional[Mapping[str, Any]],
        org: str = "public",
        reason: str = "merge_incoming_meeting_state",
    ) -> Tuple[Optional[RoomState], Dict[str, Any], bool]:
        state = self.get(session_id, org=org)
        if state is None:
            return None, dict(incoming or {}), True

        incoming = incoming or {}

        stale_session_id = str(incoming.get("session_id") or "")
        if stale_session_id and stale_session_id != session_id:
            state.stale_payloads_ignored += 1
            self._persist(state)
            self._log.error(
                "PATCH34_REVB_STALE_SESSION_STATE_IGNORED org=%s session_id=%s stale_session_id=%s room_mode=%s active_speaker_slug=%s",
                org,
                session_id,
                stale_session_id,
                state.room_mode,
                state.active_speaker_slug,
            )
            return state, state.to_dict(), False

        if incoming_state_is_empty_or_destructive(incoming):
            state.empty_state_ignored += 1
            self._persist(state)
            self._log.error(
                "PATCH34_REVB_EMPTY_MEETING_STATE_IGNORED org=%s session_id=%s room_mode=%s active_speaker_slug=%s empty_state_ignored=%s",
                org,
                session_id,
                state.room_mode,
                state.active_speaker_slug,
                state.empty_state_ignored,
            )
            return state, state.to_dict(), False

        if state.room_mode == RoomMode.TEAM.value and incoming_would_collapse_team(incoming):
            state.team_collapse_blocked += 1
            self._persist(state)
            self._log.error(
                "PATCH34_REVB_TEAM_COLLAPSE_BLOCKED org=%s session_id=%s incoming_mode=%s incoming_multi_agent_turn=%s incoming_response_control=%s room_mode=%s active_speaker_slug=%s target_agent_slugs=%s blocked_count=%s",
                org,
                session_id,
                incoming.get("mode") or incoming.get("room_mode"),
                incoming.get("multi_agent_turn"),
                incoming.get("response_control"),
                state.room_mode,
                state.active_speaker_slug,
                json.dumps(state.target_agent_slugs, ensure_ascii=False),
                state.team_collapse_blocked,
            )
            return state, state.to_dict(), False

        # Accept safe fields, but preserve invariant defaults.
        active = normalize_slug(
            incoming.get("active_speaker_slug") or incoming.get("active_persona_slug"),
            default=state.active_speaker_slug,
        )
        if active in VALID_AGENT_SLUGS:
            state.active_speaker_slug = active
            state.active_persona_slug = active
            state.active_speaker_name = display_name_for_slug(active)
            state.target_agent_slug = active

        incoming_targets = unique_valid_participants(incoming.get("target_agent_slugs") or state.target_agent_slugs)
        if state.room_mode == RoomMode.TEAM.value:
            state.target_agent_slugs = unique_valid_participants(incoming_targets)
            state.multi_agent_turn = True
            state.response_control = "room_agent_authority"

        state.transition_reason = reason
        self._persist(state)
        return state, state.to_dict(), True

    def mark_provider_switching(
        self,
        *,
        session_id: str,
        target_speaker_slug: str,
        org: str = "public",
        waited_for_idle: bool = False,
    ) -> Optional[Dict[str, Any]]:
        state = self.get(session_id, org=org)
        if not state:
            return None
        target = normalize_slug(target_speaker_slug, default=state.active_speaker_slug)
        state.pending_speaker_slug = target
        state.phase = RoomPhase.SWITCHING.value
        state.metadata["voice_update_waited_for_idle"] = bool(waited_for_idle)
        self._persist(state)
        self._log.error(
            "PATCH34_REVB_PROVIDER_SWITCHING org=%s session_id=%s target_speaker_slug=%s voice_update_waited_for_idle=%s room_state_persisted=%s",
            org,
            session_id,
            target,
            waited_for_idle,
            state.persisted,
        )
        return state.to_dict()

    def mark_provider_switch_applied(
        self,
        *,
        session_id: str,
        target_speaker_slug: str,
        org: str = "public",
        provider_session_payload_clean: bool = True,
        realtime_session_still_active: bool = True,
    ) -> Optional[Dict[str, Any]]:
        state = self.get(session_id, org=org)
        if not state:
            return None
        target = normalize_slug(target_speaker_slug, default=state.active_speaker_slug)
        if target in VALID_AGENT_SLUGS:
            state.active_speaker_slug = target
            state.active_persona_slug = target
            state.active_speaker_name = display_name_for_slug(target)
            state.target_agent_slug = target
        state.pending_speaker_slug = ""
        state.phase = RoomPhase.READY.value
        state.realtime_session_active = bool(realtime_session_still_active)
        state.metadata["agent_switch_applied"] = True
        state.metadata["provider_session_payload_clean"] = bool(provider_session_payload_clean)
        self._persist(state)
        self._log.error(
            "PATCH34_REVB_PROVIDER_SWITCH_APPLIED org=%s session_id=%s active_speaker_slug=%s agent_switch_applied=true provider_session_payload_clean=%s realtime_session_still_active=%s room_state_persisted=%s has_snapshot=%s",
            org,
            session_id,
            state.active_speaker_slug,
            provider_session_payload_clean,
            realtime_session_still_active,
            state.persisted,
            state.has_snapshot,
        )
        return state.to_dict()

    def end_room(self, *, session_id: str, org: str = "public", reason: str = "end_requested") -> Optional[Dict[str, Any]]:
        state = self.get(session_id, org=org)
        if not state:
            return None
        state.phase = RoomPhase.ENDED.value
        state.realtime_session_active = False
        state.transition_reason = reason
        self._persist(state)
        self._log.error(
            "PATCH34_REVB_ROOM_ENDED org=%s session_id=%s room_mode=%s persisted=%s has_snapshot=%s active_speaker_slug=%s version=%s",
            org,
            session_id,
            state.room_mode,
            state.persisted,
            state.has_snapshot,
            state.active_speaker_slug,
            state.version,
        )
        return state.to_dict()


# Global singleton for route-level use.
room_engine = RealtimeRoomEngine()
