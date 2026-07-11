from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


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
    requested = str(requested_agent or "").strip().lower()
    orchestrator = str(orchestrator_agent or "orkio").strip().lower()
    technical = str(technical_lead or "orion").strip().lower()

    if requested == "orion":
        return AgentTurnContext(
            requested_agent="orion",
            orchestrator_agent=orchestrator,
            turn_owner="orion",
            display_agent="orion",
            technical_lead="orion",
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
