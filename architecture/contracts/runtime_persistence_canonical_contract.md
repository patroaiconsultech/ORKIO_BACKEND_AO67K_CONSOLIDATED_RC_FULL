# Runtime Persistence Canonical Contract — EPIC-002B

Status: `shadow_only_locked`.

Baseline: `94ba9246bcd3d2a5c40d42657ae7ca17c80a2826`.

## Authority

`Runtime Persistence Layer` is the only authority allowed to derive `assistant_message_id`.

No transport, frontend, router, SSE handler, agent runtime, provider adapter or caller may supply a final `assistant_message_id`.

## Canonical Identity

The only canonical identity for assistant finalization is:

```text
thread_id + turn_id + user_message_id
```

## Deterministic Assistant Message ID

The canonical assistant message id is derived internally:

```text
assistant_message_id = "asstmsg_" + sha256(canonical_json_identity)
```

Where `canonical_json_identity` is compact JSON with explicit field names, stable key ordering and UTF-8 encoding:

```json
{"thread_id":"...","turn_id":"...","user_message_id":"..."}
```

Delimiter joins are forbidden because they can collide when identifiers contain delimiter characters such as `|`.

## Excluded Fields

The following are explicitly non-authoritative and must not participate in identity derivation:

```text
trace_id
request_id
timestamp
agent_id
model
provider
SSE event id
frontend-generated id
client-generated id
```

## Trace and Observability

`trace_id` remains valid only as observability metadata inside `PersistenceObservation`.

Retries may generate different `trace_id` values while representing the same logical turn.

## Shadow Boundary

EPIC-002B cannot perform real persistence. Any attempt to instantiate the shadow ledger with `shadow_only=False` must fail by construction.

## Duplicate and Conflict Rules

For the same canonical identity:

1. Same response hash = duplicate blocked.
2. Different response hash = conflict blocked.
3. Different trace id never creates a new assistant message id.
4. Externally supplied assistant message id is rejected.

## Rollback

Rollback is shadow-only and removes the in-memory ledger record for the canonical identity. Rollback is idempotent.

## Legacy Guard Decision

`PersistenceIdempotencyGuard` cannot remain as a second authority.

Before `guarded`, it must be one of:

1. replaced by this Runtime Persistence Layer;
2. converted into a thin compatibility adapter that delegates to this layer without deriving identity;
3. formally deprecated and removed by ADR.

It must not generate, validate, mutate or own `assistant_message_id`.


## R1 Integration Fixes

- `README.md` must not be copied over the repository root README.
- Canonical identity serialization uses compact JSON with explicit field names, not delimiter join, preventing `|` collision.


## R1 Integration Fixes

- `README.md` must not be copied over the repository root README.
- Canonical serialization uses compact JSON and not `"|".join(...)`.

## RC2-R2 Guardrail

No shim is authorized. The consolidated applier must fail closed if a pre-existing `app/config/runtime.py` path is present before write. Namespace hygiene belongs to target-only import patches, not to persistence.
