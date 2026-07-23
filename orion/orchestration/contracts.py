from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Any

@dataclass(frozen=True)
class SpecialistDefinition:
    agent_id: str
    display_name: str
    specialty: str
    capabilities: tuple[str, ...]
    enabled: bool = True

class SpecialistAgent(Protocol):
    agent_id: str
    specialty: str
    def execute(self, objective: str, inputs: list[dict[str, Any]]) -> dict[str, Any]: ...
