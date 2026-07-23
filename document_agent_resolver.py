from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable
from uuid import uuid4


@dataclass(frozen=True)
class TeamTask:
    task_id: str
    agent_id: str
    specialty: str
    objective: str


@dataclass(frozen=True)
class TeamResult:
    task_id: str
    agent_id: str
    specialty: str
    result_artifact_id: str
    summary: str
    confidence: float
    executed: bool = True


def execute_team_individually(
    *,
    agents: Iterable[Any],
    objective: str,
    execute_agent: Callable[[Any, TeamTask], dict[str, Any]],
) -> list[TeamResult]:
    """Execute every real agent separately; never simulate multiple viewpoints."""
    results: list[TeamResult] = []

    for agent in agents:
        agent_id = str(getattr(agent, "id", None) or getattr(agent, "slug", "")).strip()
        specialty = str(getattr(agent, "specialty", "") or getattr(agent, "name", "")).strip()
        if not agent_id:
            raise ValueError("team agent without id")

        task = TeamTask(
            task_id=f"task_{uuid4().hex}",
            agent_id=agent_id,
            specialty=specialty,
            objective=objective,
        )
        raw = execute_agent(agent, task)
        summary = str(raw.get("summary") or raw.get("answer") or "").strip()
        artifact_id = str(raw.get("artifact_id") or "").strip()
        confidence = float(raw.get("confidence", 0.0))

        if not artifact_id:
            raise RuntimeError(f"agent {agent_id} executed without result artifact")
        if not summary:
            raise RuntimeError(f"agent {agent_id} executed without summary")

        results.append(
            TeamResult(
                task_id=task.task_id,
                agent_id=agent_id,
                specialty=specialty,
                result_artifact_id=artifact_id,
                summary=summary,
                confidence=confidence,
                executed=True,
            )
        )

    return results
