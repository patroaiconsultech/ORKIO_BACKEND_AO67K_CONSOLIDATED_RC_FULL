# Orion R26-R27 — Artifact Engine, Operational Memory and Premium Specialist Orchestration

## Guarantees

- Every specialist must be registered with a concrete runtime adapter.
- Dispatch invokes the specialist runtime; identity-only switching is not counted as execution.
- Every call produces `agent_task` and `agent_result` artifacts.
- Every result cites `agent_id`, specialty and output artifact ID.
- Synthesis preserves disagreements instead of erasing them.
- Production execution remains forbidden.
- Human approval remains mandatory for proposals.
- Learning consumes only validated outcome artifacts and cannot alter governance.

## Runtime integration

Register existing agents through `SpecialistRuntimeAdapter`, add them to
`SpecialistRegistry`, then call `SpecialistOrchestrator.dispatch`.
The returned result artifacts are the auditable proof that the agent was used.

## Acceptance proof

A valid multi-agent cycle contains:

- N unique agent task artifact IDs
- N output artifact IDs
- N matching cited agent IDs
- one synthesis carrying all citations
- a proposal with approval required
