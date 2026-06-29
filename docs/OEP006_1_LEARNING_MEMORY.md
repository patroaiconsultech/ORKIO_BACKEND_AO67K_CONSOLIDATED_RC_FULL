# OEP-006.1 — Learning Memory

## Objective

Introduce a governed in-memory learning layer for ORKIO.

The module records learning signals from proposals, outcomes and future feedback
without executing changes automatically.

## Scope

- Backend only.
- No chat integration.
- No realtime integration.
- No database migration.
- No autonomous execution.

## Governance

Every record preserves:

- `proposal_only=True`
- `write_executed=False`
- `human_approval_required=True`

## Validation

Run:

```bash
PYTHONPATH=. python -m py_compile evolution/*.py evolution/learning_engine/*.py tests/oep006_1_learning_memory_smoke.py
PYTHONPATH=. python tests/oep006_1_learning_memory_smoke.py
```

Expected:

```txt
OEP006_1_LEARNING_MEMORY_PASS
```

## Rollback

Remove:

- `evolution/learning_engine/memory.py`
- `evolution/learning_engine/service.py`
- `tests/oep006_1_learning_memory_smoke.py`
- `docs/OEP006_1_LEARNING_MEMORY.md`
```
