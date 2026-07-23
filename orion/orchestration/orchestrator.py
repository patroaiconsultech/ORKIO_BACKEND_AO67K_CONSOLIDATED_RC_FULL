from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from typing import Any

from orion.artifacts import (
    AgentResultArtifact, AgentTaskArtifact, ArtifactEnvelope, ArtifactStore,
    default_registry, envelope_for,
)
from .policy import OrchestrationPolicy
from .registry import SpecialistRegistry

class SpecialistOrchestrator:
    """Dispatches real registered specialist runtimes and records auditable artifacts."""

    def __init__(
        self,
        registry: SpecialistRegistry,
        store: ArtifactStore,
        *,
        policy: OrchestrationPolicy | None = None,
    ) -> None:
        self.registry = registry
        self.store = store
        self.policy = policy or OrchestrationPolicy()
        self.schemas = default_registry()

    def _save(self, envelope: ArtifactEnvelope) -> ArtifactEnvelope:
        self.schemas.validate(envelope)
        self.store.save(envelope)
        return envelope

    def _dispatch_one(
        self,
        *,
        agent_id: str,
        objective: str,
        inputs: list[ArtifactEnvelope],
        cycle_id: str,
        correlation_id: str,
        requested_by: str,
    ) -> tuple[ArtifactEnvelope, ArtifactEnvelope]:
        definition = self.registry.definition(agent_id)
        task = AgentTaskArtifact(
            requested_by=requested_by,
            assigned_agent=agent_id,
            specialty=definition.specialty,
            objective=objective,
            input_artifact_ids=tuple(item.artifact_id for item in inputs),
            status="dispatched",
        )
        task_env = self._save(envelope_for(
            "agent_task", task, cycle_id=cycle_id, correlation_id=correlation_id,
            producer="orion.orchestration", parents=tuple(item.artifact_id for item in inputs),
            metadata={"display_name": definition.display_name},
        ))

        try:
            runtime = self.registry.get(agent_id)
            raw = runtime.execute(objective, [item.to_dict() for item in inputs])
            result = AgentResultArtifact(
                task_id=task_env.artifact_id,
                agent_id=agent_id,
                specialty=definition.specialty,
                summary=str(raw.get("summary", "")).strip(),
                findings=tuple(raw.get("findings", ())),
                confidence=float(raw.get("confidence", 0.0)),
                cited_agent=agent_id,
                evidence_ids=tuple(raw.get("evidence_ids", ())),
            )
            result_env = self._save(envelope_for(
                "agent_result", result, cycle_id=cycle_id, correlation_id=correlation_id,
                producer=agent_id, parents=(task_env.artifact_id,),
                metadata={"agent_display_name": definition.display_name, "executed": True},
            ))
            return task_env, result_env
        except Exception as exc:
            failed = replace(task, status="failed", error=type(exc).__name__)
            # Preserve the original immutable task and add a failure result.
            result = AgentResultArtifact(
                task_id=task_env.artifact_id,
                agent_id=agent_id,
                specialty=definition.specialty,
                summary="Specialist execution failed safely.",
                findings=({"error_type": type(exc).__name__},),
                confidence=0.0,
                cited_agent=agent_id,
            )
            result_env = self._save(envelope_for(
                "agent_result", result, cycle_id=cycle_id, correlation_id=correlation_id,
                producer=agent_id, parents=(task_env.artifact_id,),
                metadata={"executed": True, "failed": True, "task_status": failed.status},
            ))
            if not self.policy.continue_on_partial_failure:
                raise
            return task_env, result_env

    def dispatch(
        self,
        *,
        agent_ids: list[str],
        objective: str,
        inputs: list[ArtifactEnvelope],
        cycle_id: str,
        correlation_id: str,
        requested_by: str = "orion",
        environment: str = "readonly",
    ) -> list[tuple[ArtifactEnvelope, ArtifactEnvelope]]:
        self.policy.assert_environment(environment)
        ordered_ids = list(dict.fromkeys(agent_ids))
        if not ordered_ids:
            raise ValueError("at_least_one_specialist_required")
        if len(ordered_ids) > self.policy.max_specialists:
            raise ValueError("specialist_limit_exceeded")

        if not self.policy.allow_parallel or len(ordered_ids) == 1:
            return [self._dispatch_one(
                agent_id=agent_id, objective=objective, inputs=inputs,
                cycle_id=cycle_id, correlation_id=correlation_id, requested_by=requested_by,
            ) for agent_id in ordered_ids]

        completed: dict[str, tuple[ArtifactEnvelope, ArtifactEnvelope]] = {}
        with ThreadPoolExecutor(max_workers=len(ordered_ids)) as pool:
            futures = {
                pool.submit(
                    self._dispatch_one,
                    agent_id=agent_id, objective=objective, inputs=inputs,
                    cycle_id=cycle_id, correlation_id=correlation_id, requested_by=requested_by,
                ): agent_id for agent_id in ordered_ids
            }
            for future in as_completed(futures, timeout=self.policy.timeout_seconds):
                completed[futures[future]] = future.result()
        return [completed[agent_id] for agent_id in ordered_ids]
