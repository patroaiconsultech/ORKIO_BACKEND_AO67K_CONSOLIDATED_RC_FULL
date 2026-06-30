# CP-002 — Mission Kernel

## Capability
Mission Kernel

## Objective
Introduce Mission as the primary domain entity of ORKIO OS.

## Scope
This capability defines the initial Mission domain model and its contract.

## Out of Scope
- Runtime changes
- Database persistence
- API endpoints
- Frontend changes
- LLM behavior changes
- Planner
- Memory
- Evidence engine

## Architecture Rules
- Mission is the primary domain entity.
- Conversation is an interaction channel and may become an event stream.
- Every persistent cognitive artifact should belong to a Mission.
- The LLM never owns Mission State.
- Mission state is controlled by ORKIO OS runtime/domain logic.

## Acceptance Criteria
- Mission domain model exists.
- Mission status and stage are explicit.
- Mission summary, context and health are representable.
- Tests validate the domain contract.
- Runtime remains untouched.
