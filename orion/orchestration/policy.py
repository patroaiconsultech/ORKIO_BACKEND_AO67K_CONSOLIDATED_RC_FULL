from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class OrchestrationPolicy:
    max_specialists: int = 5
    timeout_seconds: int = 60
    allow_parallel: bool = True
    require_agent_citation: bool = True
    require_output_artifact: bool = True
    continue_on_partial_failure: bool = True
    allowed_environments: tuple[str, ...] = ("readonly", "simulation", "sandbox")

    def assert_environment(self, environment: str) -> None:
        if environment not in self.allowed_environments:
            raise PermissionError("orchestration_environment_forbidden")
