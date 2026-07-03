# ADR-0003 — Runtime Persistence Canonical Assistant Message ID

## Status

Accepted for shadow branch only.

## Context

EPIC-002A removed `trace_id` from the canonical idempotency key, but still allowed `assistant_message_id` to be supplied by callers.

That left a remaining authority leak: two independent callers could attempt to finalize the same logical turn with different assistant ids.

## Decision

`Runtime Persistence Layer` is the only authority for `assistant_message_id`.

The canonical assistant message id is:

```text
asstmsg_ + sha256(compact canonical JSON identity)
```

Callers cannot supply `assistant_message_id`.

## Consequences

- Same logical turn always derives the same `assistant_message_id`.
- Retries with different `trace_id` values cannot create new assistant ids.
- External assistant ids are rejected.
- Conflicting responses for the same logical turn are blocked.
- Shadow rollback is safe and idempotent.
- No production side effects are introduced.

## Legacy Compatibility

`PersistenceIdempotencyGuard` remains a baseline artifact only until guarded migration.

It cannot remain as an authority. It must be adapted, replaced or deprecated before `guarded`.


## R1 Integration Fixes

- `README.md` must not be copied over the repository root README.
- Canonical identity serialization uses compact JSON with explicit field names, not delimiter join, preventing `|` collision.


## R1 Addendum

Delimiter-based serialization is forbidden. Canonical identity is serialized as compact JSON with explicit keys and stable ordering to prevent delimiter collision.


## RC2-R2 Guardrail

No shim is authorized. The consolidated applier must fail closed if a pre-existing `app/config/runtime.py` path is present before write. Namespace hygiene belongs to target-only import patches, not to persistence.
