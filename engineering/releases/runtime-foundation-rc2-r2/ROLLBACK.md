# Rollback — ORKIO CORE RC2 Runtime Foundation

## Preferred rollback

Use Git:

```bash
git restore runtime/orkio_runtime_foundation/persistence.py
git restore runtime/intent_engine.py
git restore services/governance_service.py
git restore services/capability_service.py
git restore tests/runtime/test_runtime_persistence_shadow.py
git restore architecture/contracts/runtime_persistence_canonical_contract.md
git restore engineering/EPIC002B_CANONICAL_ASSISTANT_MESSAGE_ID_SHADOW_LOCKED.md
git restore engineering/VALIDACAO_LOCAL_EPIC002B.md
git restore adrs/ADR-0003-runtime-persistence-canonical-assistant-message-id.md
```

Or reset the branch if this RC2 is the only commit.

## Impact

No DB rollback required.
No SSE rollback required.
No main.py rollback expected.
