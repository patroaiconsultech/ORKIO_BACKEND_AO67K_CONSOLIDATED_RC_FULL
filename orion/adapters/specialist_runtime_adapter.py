from __future__ import annotations
from typing import Any, Callable

class SpecialistRuntimeAdapter:
    """Wraps an existing real agent callable without simulating its execution."""

    def __init__(self, agent_id: str, specialty: str, runtime: Callable[[str, list[dict[str, Any]]], dict[str, Any]]) -> None:
        self.agent_id = agent_id
        self.specialty = specialty
        self._runtime = runtime

    def execute(self, objective: str, inputs: list[dict[str, Any]]) -> dict[str, Any]:
        result = self._runtime(objective, inputs)
        if not isinstance(result, dict):
            raise TypeError("specialist_runtime_must_return_dict")
        return result
