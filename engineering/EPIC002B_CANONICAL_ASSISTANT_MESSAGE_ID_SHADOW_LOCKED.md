# EPIC-002B — Canonical Assistant Message ID Shadow Locked

## Objective

Resolve permanently the EPIC-002B blockers:

- canonical `assistant_message_id`
- deterministic derivation
- single persistence contract
- removal of duplicate identity authority
- executable tests
- ADR update

## Scope

Shadow only.

## Changes

- `assistant_message_id` is no longer accepted from callers.
- `assistant_message_id` is derived inside `Runtime Persistence Layer`.
- Deterministic derivation uses the canonical tuple:

```text
compact_json(thread_id, turn_id, user_message_id)
```

- `trace_id` remains observability-only.
- Concurrent retries are protected by an in-memory lock.
- Shadow rollback is idempotent.
- Tests validate identity, idempotency, concurrency, rollback and SSE compatibility.

## Non-Goals

- No `main.py` changes.
- No runtime production integration.
- No database writes.
- No frontend changes.
- No SSE changes.
- No new router.
- No new guard.
- No new authority.

## Files

```text
runtime/orkio_runtime_foundation/persistence.py
tests/runtime/test_runtime_persistence_shadow.py
architecture/contracts/runtime_persistence_canonical_contract.md
engineering/EPIC002B_CANONICAL_ASSISTANT_MESSAGE_ID_RC2_RUNTIME_FOUNDATION.md
adrs/ADR-0003-runtime-persistence-canonical-assistant-message-id.md
README.md
MAPA_DE_IMPLANTACAO.md
```

## Status

GO for branch/shadow audit.

NO-GO for guarded, enforcement or production until independent audit approves the migration path from any legacy `PersistenceIdempotencyGuard`.


## R1 Integration Fixes

- `README.md` must not be copied over the repository root README.
- Canonical identity serialization uses compact JSON with explicit field names, not delimiter join, preventing `|` collision.


## R1 Mandatory Corrections

- Root `README.md` removed from copy list in `MAPA_DE_IMPLANTACAO.md`.
- Canonical key serialization changed from delimiter join to compact JSON to prevent collision.
- Test suite increased to 12 tests, including delimiter collision forensics.

## RC2-R2 Guardrail

No shim is authorized. The consolidated applier must fail closed if a pre-existing `app/config/runtime.py` path is present before write. Namespace hygiene belongs to target-only import patches, not to persistence.
