from orion.artifacts import ArtifactStore, EvidenceArtifact, envelope_for
from orion.orchestration import (
    SpecialistDefinition, SpecialistOrchestrator, SpecialistRegistry, SynthesisEngine,
)

class RealAgent:
    def __init__(self, agent_id, specialty):
        self.agent_id = agent_id
        self.specialty = specialty
        self.calls = 0
    def execute(self, objective, inputs):
        self.calls += 1
        return {
            "summary": f"{self.agent_id} executed {objective}",
            "findings": [{"topic":"runtime","conclusion":self.agent_id}],
            "confidence": 0.9,
        }

def test_specialists_are_really_called_and_cited(tmp_path):
    registry = SpecialistRegistry()
    agents = [RealAgent("backend_specialist","backend"), RealAgent("sse_specialist","runtime_sse")]
    for agent in agents:
        registry.register(
            SpecialistDefinition(agent.agent_id, agent.agent_id, agent.specialty, ("audit",)),
            agent,
        )
    evidence = envelope_for(
        "evidence", EvidenceArtifact("log","request","stream request entered",1.0),
        cycle_id="c1", correlation_id="r1", producer="test",
    )
    orchestrator = SpecialistOrchestrator(registry, ArtifactStore(tmp_path))
    executions = orchestrator.dispatch(
        agent_ids=[a.agent_id for a in agents], objective="audit stream",
        inputs=[evidence], cycle_id="c1", correlation_id="r1",
    )
    results = [result for _, result in executions]
    assert [a.calls for a in agents] == [1, 1]
    assert all(result.metadata["executed"] is True for result in results)
    synthesis = SynthesisEngine().synthesize("audit stream", results)
    assert {c.agent_id for c in synthesis.citations} == {"backend_specialist","sse_specialist"}
    assert all(c.result_artifact_id for c in synthesis.citations)
