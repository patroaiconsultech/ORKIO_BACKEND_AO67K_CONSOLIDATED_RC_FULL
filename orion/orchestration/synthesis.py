from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from orion.artifacts import ArtifactEnvelope

@dataclass(frozen=True)
class SpecialistCitation:
    agent_id: str
    specialty: str
    result_artifact_id: str
    summary: str
    confidence: float

@dataclass(frozen=True)
class OrchestrationSynthesis:
    objective: str
    citations: tuple[SpecialistCitation, ...]
    findings: tuple[dict[str, Any], ...]
    disagreements: tuple[dict[str, Any], ...]

class SynthesisEngine:
    def synthesize(self, objective: str, results: list[ArtifactEnvelope]) -> OrchestrationSynthesis:
        citations: list[SpecialistCitation] = []
        findings: list[dict[str, Any]] = []
        for envelope in results:
            if envelope.artifact_type != "agent_result":
                raise ValueError("agent_result_required")
            payload = envelope.payload
            if payload.get("agent_id") != payload.get("cited_agent"):
                raise ValueError("uncited_specialist_result")
            citations.append(SpecialistCitation(
                agent_id=payload["agent_id"],
                specialty=payload["specialty"],
                result_artifact_id=envelope.artifact_id,
                summary=payload["summary"],
                confidence=float(payload["confidence"]),
            ))
            for finding in payload.get("findings", ()):
                findings.append({"agent_id": payload["agent_id"], **dict(finding)})
        # Divergence is preserved rather than silently collapsed.
        by_key: dict[str, set[str]] = {}
        for finding in findings:
            key = str(finding.get("topic", finding.get("type", "general")))
            by_key.setdefault(key, set()).add(str(finding.get("conclusion", finding)))
        disagreements = tuple(
            {"topic": key, "positions": tuple(sorted(values))}
            for key, values in by_key.items() if len(values) > 1
        )
        return OrchestrationSynthesis(
            objective=objective,
            citations=tuple(citations),
            findings=tuple(findings),
            disagreements=disagreements,
        )
