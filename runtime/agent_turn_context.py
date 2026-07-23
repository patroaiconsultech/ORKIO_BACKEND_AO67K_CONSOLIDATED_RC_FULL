from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


EXPLICIT_TURN_OWNER_SLUGS = frozenset({"orkio", "orion", "chris", "laura"})


@dataclass(frozen=True)
class AgentTurnContext:
    requested_agent: str
    orchestrator_agent: str
    turn_owner: str
    display_agent: str
    technical_lead: str
    route_family: str
    ownership_locked: bool

    @property
    def agent_id(self) -> str:
        return self.display_agent.strip().lower()

    @property
    def agent_name(self) -> str:
        return self.display_agent.strip().title()

    def to_routing_payload(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["agent_id"] = self.agent_id
        payload["agent_name"] = self.agent_name
        return payload


def resolve_agent_turn_context(
    requested_agent: Optional[str],
    *,
    route_family: str,
    orchestrator_agent: str = "orkio",
    technical_lead: str = "orion",
) -> AgentTurnContext:
    requested = str(requested_agent or "").strip().lower().lstrip("@")
    orchestrator = str(orchestrator_agent or "orkio").strip().lower()
    technical = str(technical_lead or "orion").strip().lower()

    # R22: an explicit, registered destination owns the whole turn.
    # The same canonical identity must be used by routing, SSE, persistence
    # and frontend presentation. Team remains outside this lock until its
    # execution contract is proven end-to-end.
    if requested in EXPLICIT_TURN_OWNER_SLUGS:
        return AgentTurnContext(
            requested_agent=requested,
            orchestrator_agent=orchestrator,
            turn_owner=requested,
            display_agent=requested,
            technical_lead="orion" if requested == "orion" else technical,
            route_family=route_family,
            ownership_locked=True,
        )

    return AgentTurnContext(
        requested_agent=requested or orchestrator,
        orchestrator_agent=orchestrator,
        turn_owner=orchestrator,
        display_agent=orchestrator,
        technical_lead=technical,
        route_family=route_family,
        ownership_locked=False,
    )


def explicit_turn_owner_candidate(*values: Any) -> Optional[str]:
    """Return the explicit registered owner already present in request metadata."""
    for value in values:
        if value is None:
            continue

        if isinstance(value, (list, tuple, set)):
            nested = explicit_turn_owner_candidate(*list(value))
            if nested:
                return nested
            continue

        raw = str(value or "").strip().lower().lstrip("@")
        if raw in EXPLICIT_TURN_OWNER_SLUGS:
            return raw

    return None


def stream_turn_owner_from_contract(
    *,
    admin_bypass_agent: Any = None,
    route_plan: Optional[Dict[str, Any]] = None,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
    agent_id: Any = None,
    requested_agent_names: Any = None,
    target_agent_slugs: Any = None,
    agent_ids: Any = None,
) -> Optional[str]:
    """Resolve immutable stream owner from destination contract plus route output."""
    route = route_plan if isinstance(route_plan, dict) else {}
    return explicit_turn_owner_candidate(
        admin_bypass_agent,
        visible_agent,
        target_agent_slug,
        agent_id,
        requested_agent_names,
        target_agent_slugs,
        agent_ids,
        route.get("requested_agent"),
        route.get("resolved_agent"),
        route.get("target_agent"),
        route.get("agent"),
    )
