from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any


@dataclass(frozen=True)
class PlanDependencyGraph:
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    has_cycles: bool = False
    proposal_only: bool = True
    write_executed: bool = False
    human_approval_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class PlanDependencyGraphBuilder:
    """Builds a deterministic dependency graph for plan steps.

    No execution is performed. This is a structural analysis layer only.
    """

    def build(self, plan: Any) -> dict[str, Any]:
        data = plan.to_dict() if hasattr(plan, "to_dict") else dict(plan)
        steps = data.get("steps", []) or []

        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []

        previous_id: str | None = None
        seen: set[str] = set()
        has_cycles = False

        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                continue
            step_id = str(step.get("step_id") or f"step_{index + 1}")
            if step_id in seen:
                has_cycles = True
            seen.add(step_id)

            nodes.append({
                "id": step_id,
                "title": step.get("title", ""),
                "risk": step.get("risk", "low"),
                "status": step.get("status", "proposed"),
            })

            dependencies = step.get("dependencies") or step.get("depends_on") or []
            if isinstance(dependencies, str):
                dependencies = [dependencies]

            for dep in dependencies:
                edges.append({"from": str(dep), "to": step_id, "type": "declared_dependency"})

            if previous_id and not dependencies:
                edges.append({"from": previous_id, "to": step_id, "type": "sequence"})
            previous_id = step_id

        return PlanDependencyGraph(nodes=nodes, edges=edges, has_cycles=has_cycles).to_dict()
