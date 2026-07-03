# Diff Summary — RC2 Runtime Foundation

Expected productive diff after application:

```text
A/M runtime/orkio_runtime_foundation/persistence.py
M   runtime/intent_engine.py
M   services/governance_service.py
M   services/capability_service.py
A/M tests/runtime/test_runtime_persistence_shadow.py
A/M architecture/contracts/runtime_persistence_canonical_contract.md
A/M engineering/EPIC002B_CANONICAL_ASSISTANT_MESSAGE_ID_SHADOW_LOCKED.md
A/M engineering/VALIDACAO_LOCAL_EPIC002B.md
A/M adrs/ADR-0003-runtime-persistence-canonical-assistant-message-id.md
```

Forbidden productive diff:

```text
M main.py
M routes/realtime.py
DB migrations
SSE contract changes
```
