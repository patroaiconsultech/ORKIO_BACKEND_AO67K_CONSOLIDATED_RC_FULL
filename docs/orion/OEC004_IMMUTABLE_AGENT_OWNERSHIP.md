# OEC-004 — Immutable Agent Ownership

## Objective

Prevent contextual continuity, fast-paths, persistence and final SSE envelopes
from replacing an explicitly selected agent.

## Root cause

AO45A used `route_plan.requested_agent` as a local protection. That field is not
the canonical source of ownership. The canonical source is `AgentTurnContext`.

## Minimal layer

AO45A consults `should_allow_chris_context_continuity()` before loading Chris
context. If Orion owns the locked turn, AO45A is skipped.

## Premium layer

1. `_persist_assistant_message()` normalizes `agent_id` and `agent_name` from
   the immutable turn context.
2. Same-turn duplicate messages have ownership metadata reconciled.
3. `_emit_result_payload()` normalizes `agent_id`, `agent_name`,
   `final_speaker`, `visible_agent` and `speaker_name`.
4. Routing metadata records ownership and the enforcement version.

## Non-goals

This patch does not change:
- routing intent;
- proposal creation;
- Mutation Authority;
- GitHub permissions;
- merge or deploy;
- database schema;
- frontend rendering.

## Expected logs

For Orion selected with recent Chris context:

```
AO45A_CHRIS_CONTEXT_CONTINUITY_SKIPPED ... reason=explicit_non_chris_owner
OEC004_PERSISTENCE_OWNER_ENFORCED ... agent_id=orion agent_name=Orion
OEC004_FINAL_ENVELOPE_OWNER_ENFORCED ... turn_owner=orion
```

## Validation

```
pytest -q tests/test_oec004_agent_ownership_enforcement.py
```

Expected: `5 passed`.

## Rollback

Restore `main.py` and remove
`runtime/agent_ownership_enforcement.py` plus the OEC-004 test and docs.
No database rollback is required.
