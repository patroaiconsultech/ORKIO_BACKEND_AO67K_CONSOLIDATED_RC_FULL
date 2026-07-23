from __future__ import annotations
from .contracts import SpecialistAgent, SpecialistDefinition

class SpecialistRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, SpecialistDefinition] = {}
        self._agents: dict[str, SpecialistAgent] = {}

    def register(self, definition: SpecialistDefinition, agent: SpecialistAgent) -> None:
        if definition.agent_id != agent.agent_id:
            raise ValueError("specialist_identity_mismatch")
        if not definition.enabled:
            raise ValueError("cannot_register_disabled_specialist")
        if definition.agent_id in self._agents:
            raise ValueError("specialist_already_registered")
        self._definitions[definition.agent_id] = definition
        self._agents[definition.agent_id] = agent

    def get(self, agent_id: str) -> SpecialistAgent:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(f"specialist_not_registered:{agent_id}") from exc

    def definition(self, agent_id: str) -> SpecialistDefinition:
        return self._definitions[agent_id]

    def available(self) -> tuple[SpecialistDefinition, ...]:
        return tuple(self._definitions.values())
