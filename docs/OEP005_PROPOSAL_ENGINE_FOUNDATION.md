# OEP-005 — Proposal Engine Foundation

Backend-only foundation for deterministic, governed proposal packages.

## Validation

```bash
PYTHONPATH=. python -m py_compile evolution/*.py evolution/proposal_engine/*.py tests/oep005_proposal_engine_smoke.py
PYTHONPATH=. python tests/oep005_proposal_engine_smoke.py
```

Expected:

```text
OEP005_PROPOSAL_ENGINE_FOUNDATION_PASS
```

## Guarantees

- proposal_only = true
- requires_human_approval = true
- write_executed = false
- no automatic execution
