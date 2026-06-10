from __future__ import annotations

"""
AO67H — Realtime Orchestration Policy

Purpose:
- Public/AMCHAM realtime must be Orkio-only and multimodal.
- Founder/admin realtime may target direct agents or a meeting room.
- The policy itself does not open sockets, call OpenAI, write DB, or deploy.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

try:
    from app.services.admin_agent_access_service import (
        PUBLIC_SPEAKER,
        decide_agent_access,
        normalize_agent_list,
        normalize_agent_slug,
        is_admin_surface,
    )
except Exception:  # pragma: no cover
    PUBLIC_SPEAKER = "Orkio"

    def normalize_agent_slug(v: Any) -> str:
        return str(v or "orkio").strip().lower().replace("@", "") or "orkio"

    def normalize_agent_list(v: Any) -> List[str]:
        return []

    def is_admin_surface(v: Any) -> bool:
        return str(v or "").strip().lower() in {"admin", "founder", "founder_admin", "founder-admin", "internal", "operator", "admin_room", "admin_agent_room", "founder_room", "founder_agent_room"}

    def decide_agent_access(*args: Any, **kwargs: Any):
        class D:
            ok = True
            public_surface = True
            admin_surface = False
            can_realtime = False
            can_see_internal_name = False
            resolved_internal_agent = "orkio"
            warnings = []
            reason = "fallback"

            def to_dict(self) -> Dict[str, Any]:
                return self.__dict__.copy()
        return D()


DEFAULT_REALTIME_MODEL = "gpt-realtime-mini"
DEFAULT_REALTIME_VOICE = "cedar"
REQUIRED_PUBLIC_MODALITIES = ("audio", "text")


@dataclass(frozen=True)
class RealtimeOrchestrationDecision:
    ok: bool
    surface: str
    mode: str
    public_speaker: str = PUBLIC_SPEAKER
    internal_agent: str = "orkio"
    requested_agents: List[str] = field(default_factory=list)
    admin_visible_agents: List[str] = field(default_factory=list)
    public_visible_agents: List[str] = field(default_factory=lambda: [PUBLIC_SPEAKER])
    model: str = DEFAULT_REALTIME_MODEL
    voice: str = DEFAULT_REALTIME_VOICE
    modalities: List[str] = field(default_factory=lambda: list(REQUIRED_PUBLIC_MODALITIES))
    response_profile: str = "orkio_public_realtime"
    language_profile: str = "pt-BR"
    instructions_contract: str = "public_orkio_only"
    commit_memory: bool = False
    can_open_session: bool = True
    warnings: List[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _payload_get(payload: Any, key: str, default: Any = None) -> Any:
    if payload is None:
        return default
    if isinstance(payload, dict):
        return payload.get(key, default)
    return getattr(payload, key, default)


def build_realtime_orchestration_decision(
    payload: Any,
    *,
    requested_agent: Any = None,
    requested_agents: Any = None,
    surface: str = "public",
    mode: str = "platform",
    voice: Optional[str] = None,
    model: Optional[str] = None,
    language_profile: Optional[str] = None,
    response_profile: Optional[str] = None,
    room: bool = False,
    commit_memory: bool = False,
    **_: Any,
) -> RealtimeOrchestrationDecision:
    norm_surface = _clean(surface).lower() or "public"
    public_surface = not is_admin_surface(norm_surface)
    warnings: List[str] = []

    selected_agents = normalize_agent_list(requested_agents)
    selected_agent = normalize_agent_slug(requested_agent or "") if requested_agent else ""
    if selected_agent and selected_agent not in selected_agents:
        selected_agents.insert(0, selected_agent)

    if public_surface:
        if selected_agents and any(a != "orkio" for a in selected_agents):
            warnings.append("public_realtime_internal_agent_request_masked")
        return RealtimeOrchestrationDecision(
            ok=True,
            surface="public",
            mode="public_orkio_only",
            public_speaker=PUBLIC_SPEAKER,
            internal_agent="orkio",
            requested_agents=["orkio"],
            admin_visible_agents=[],
            public_visible_agents=[PUBLIC_SPEAKER],
            model=model or DEFAULT_REALTIME_MODEL,
            voice=voice or DEFAULT_REALTIME_VOICE,
            modalities=list(REQUIRED_PUBLIC_MODALITIES),
            response_profile=response_profile or "amcham_public_orkio_realtime",
            language_profile=language_profile or "pt-BR",
            instructions_contract="amcham_public_orkio_only_audio_text",
            commit_memory=False,
            can_open_session=True,
            warnings=warnings,
            reason="public_realtime_orkio_only",
        )

    if not selected_agents:
        selected_agents = ["orkio", "chris", "orion"] if room else ["orkio"]

    admin_visible: List[str] = []
    internal_agent = "orkio"

    for agent in selected_agents:
        decision = decide_agent_access(payload, agent, mode="realtime", surface="admin")
        if not getattr(decision, "ok", False) or not getattr(decision, "can_realtime", False):
            warnings.extend(list(getattr(decision, "warnings", []) or []))
            continue
        resolved = str(getattr(decision, "resolved_internal_agent", agent) or agent)
        admin_visible.append(resolved)
        if internal_agent == "orkio":
            internal_agent = resolved

    if not admin_visible:
        return RealtimeOrchestrationDecision(
            ok=False,
            surface="admin",
            mode="admin_realtime_denied",
            internal_agent="orkio",
            requested_agents=selected_agents,
            model=model or DEFAULT_REALTIME_MODEL,
            voice=voice or DEFAULT_REALTIME_VOICE,
            modalities=list(REQUIRED_PUBLIC_MODALITIES),
            response_profile=response_profile or "admin_realtime",
            language_profile=language_profile or "pt-BR",
            instructions_contract="admin_realtime_denied",
            commit_memory=False,
            can_open_session=False,
            warnings=warnings or ["no_authorized_realtime_agent"],
            reason="no_authorized_realtime_agent",
        )

    return RealtimeOrchestrationDecision(
        ok=True,
        surface="admin",
        mode="admin_meeting_room_realtime" if len(admin_visible) > 1 else "admin_direct_agent_realtime",
        public_speaker=PUBLIC_SPEAKER,
        internal_agent=internal_agent,
        requested_agents=selected_agents,
        admin_visible_agents=admin_visible,
        public_visible_agents=[PUBLIC_SPEAKER],
        model=model or DEFAULT_REALTIME_MODEL,
        voice=voice or DEFAULT_REALTIME_VOICE,
        modalities=list(REQUIRED_PUBLIC_MODALITIES),
        response_profile=response_profile or "admin_agent_realtime",
        language_profile=language_profile or "pt-BR",
        instructions_contract="admin_visible_agent_room_audio_text",
        commit_memory=bool(commit_memory),
        can_open_session=True,
        warnings=warnings,
        reason="admin_realtime_policy_ready",
    )


def public_realtime_request_payload(**kwargs: Any) -> Dict[str, Any]:
    decision = build_realtime_orchestration_decision(None, surface="public", **kwargs)
    return {
        "agent_id": None,
        "thread_id": kwargs.get("thread_id"),
        "voice": decision.voice,
        "model": decision.model,
        "mode": decision.mode,
        "response_profile": decision.response_profile,
        "language_profile": decision.language_profile,
        "modalities": decision.modalities,
        "public_speaker": decision.public_speaker,
        "instructions_contract": decision.instructions_contract,
    }
