from __future__ import annotations

"""
AO67H — Founder/Admin Agent Room

Purpose:
- Let Daniel/admin speak directly with any agent or sub-agent for testing.
- Let the three principal agents contribute simultaneously like a boardroom.
- Keep public/AMCHAM surface Orkio-only.
- No LLM call, no DB write, no network call.

This module produces an orchestration plan. Future wiring may call model providers.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Iterable, List, Optional

try:
    from app.services.admin_agent_access_service import (
        PUBLIC_SPEAKER,
        decide_agent_access,
        normalize_agent_list,
        normalize_agent_slug,
    )
except Exception:  # pragma: no cover
    PUBLIC_SPEAKER = "Orkio"

    def normalize_agent_slug(v: Any) -> str:
        return str(v or "orkio").strip().lower().replace("@", "") or "orkio"

    def normalize_agent_list(values: Any) -> List[str]:
        if values is None:
            return []
        if isinstance(values, str):
            return [normalize_agent_slug(x) for x in values.split(",") if normalize_agent_slug(x)]
        return [normalize_agent_slug(x) for x in values if normalize_agent_slug(x)]

    def decide_agent_access(*args: Any, **kwargs: Any):
        class D:
            ok = False
            can_direct = False
            can_room = False
            can_realtime = False
            can_see_internal_name = False
            reason = "access_service_unavailable"
            warnings = ["access_service_unavailable"]

            def to_dict(self) -> Dict[str, Any]:
                return self.__dict__.copy()
        return D()


PRINCIPAL_AGENT_COUNCIL = ("orkio", "chris", "orion")


@dataclass(frozen=True)
class AgentRoomParticipant:
    slug: str
    role: str
    visible_to_admin: bool
    visible_to_public: bool
    public_speaker: str = PUBLIC_SPEAKER
    contribution_mode: str = "advice_only"


@dataclass(frozen=True)
class FounderAgentRoomPlan:
    ok: bool
    room_id: str
    mode: str
    surface: str
    requested_agents: List[str]
    participants: List[AgentRoomParticipant]
    public_speaker: str = PUBLIC_SPEAKER
    synthesis_owner: str = "orkio"
    parallel: bool = True
    realtime_supported: bool = True
    public_visible_names: List[str] = field(default_factory=lambda: [PUBLIC_SPEAKER])
    admin_visible_names: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        out = asdict(self)
        out["participants"] = [asdict(p) for p in self.participants]
        return out


def _role_for(slug: str) -> str:
    if slug == "orkio":
        return "chief_synthesis_and_decision"
    if slug == "chris":
        return "business_finance_strategy_advisor"
    if slug == "orion":
        return "technical_architecture_runtime_advisor"
    if slug == "auditor":
        return "governance_audit_advisor"
    if slug in {"cfo", "finance"}:
        return "financial_advisor"
    if slug in {"cto", "architect"}:
        return "technical_advisor"
    return "specialist_subagent_advisor"


def default_principal_room_agents() -> List[str]:
    return list(PRINCIPAL_AGENT_COUNCIL)


def build_founder_agent_room_plan(
    payload: Any,
    *,
    agents: Any = None,
    message: str = "",
    surface: str = "admin",
    mode: str = "meeting",
    realtime: bool = False,
    allow_subagents: bool = True,
    **_: Any,
) -> FounderAgentRoomPlan:
    """
    Build a safe plan for a founder/admin meeting room.

    Admin/founder:
    - Can see the selected agent names.
    - Can ask direct questions.
    - Can run a 3-agent room: Orkio + Chris + Orion.

    Public:
    - Always receives Orkio-only synthesis.
    """
    norm_surface = str(surface or "admin").strip().lower()
    requested = normalize_agent_list(agents)
    if not requested:
        requested = default_principal_room_agents()

    participants: List[AgentRoomParticipant] = []
    warnings: List[str] = []
    any_denied = False

    for slug in requested:
        decision = decide_agent_access(
            payload,
            slug,
            mode="realtime" if realtime else mode,
            surface=norm_surface,
            allow_subagents=allow_subagents,
        )
        if not getattr(decision, "ok", False):
            any_denied = True
            warnings.extend(list(getattr(decision, "warnings", []) or []))
            continue

        visible_admin = bool(getattr(decision, "can_see_internal_name", False))
        visible_public = False if slug != "orkio" else norm_surface == "public"
        participants.append(
            AgentRoomParticipant(
                slug=slug if visible_admin else "orkio",
                role=_role_for(slug),
                visible_to_admin=visible_admin,
                visible_to_public=visible_public,
                public_speaker=PUBLIC_SPEAKER,
                contribution_mode="advice_only" if slug != "orkio" else "decision_and_synthesis",
            )
        )
        warnings.extend(list(getattr(decision, "warnings", []) or []))

    if norm_surface == "public":
        participants = [
            AgentRoomParticipant(
                slug="orkio",
                role=_role_for("orkio"),
                visible_to_admin=False,
                visible_to_public=True,
                public_speaker=PUBLIC_SPEAKER,
                contribution_mode="decision_and_synthesis",
            )
        ]

    admin_visible_names = [p.slug for p in participants if p.visible_to_admin]
    if not participants:
        return FounderAgentRoomPlan(
            ok=False,
            room_id="",
            mode=mode,
            surface=norm_surface,
            requested_agents=requested,
            participants=[],
            parallel=False,
            realtime_supported=False,
            admin_visible_names=[],
            warnings=warnings or ["no_authorized_participants"],
            reason="no_authorized_participants",
        )

    return FounderAgentRoomPlan(
        ok=not any_denied or bool(participants),
        room_id="founder-room-draft",
        mode=mode,
        surface=norm_surface,
        requested_agents=requested,
        participants=participants,
        public_speaker=PUBLIC_SPEAKER,
        synthesis_owner="orkio",
        parallel=len(participants) > 1,
        realtime_supported=True,
        public_visible_names=[PUBLIC_SPEAKER],
        admin_visible_names=admin_visible_names,
        warnings=warnings,
        reason="founder_room_plan_ready" if norm_surface != "public" else "public_surface_orkio_only",
    )


def build_admin_direct_agent_plan(
    payload: Any,
    *,
    agent: Any,
    message: str = "",
    realtime: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    slug = normalize_agent_slug(agent) or "orkio"
    plan = build_founder_agent_room_plan(
        payload,
        agents=[slug],
        message=message,
        surface="admin",
        mode="direct",
        realtime=realtime,
        **kwargs,
    )
    out = plan.to_dict()
    out["direct_agent"] = slug
    return out
