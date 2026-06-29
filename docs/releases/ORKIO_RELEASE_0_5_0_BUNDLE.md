# ORKIO Release 0.5.0 Bundle

## Scope

This bundle adds modular proposal-engine extensions and a first learning-engine foundation.

## Included OEPs

- OEP-004.4 — Regression Suite
- OEP-005.1 — Proposal Ranking
- OEP-005.2 — Conflict Detection
- OEP-005.3 — Human Approval Workflow
- OEP-006 — Learning Engine Foundation

## Governance

All new modules preserve:

- `proposal_only=True`
- `requires_human_approval=True`
- no automatic production execution

## Validation

Run:

```bash
PYTHONPATH=. python tests/regression/run_regression_suite.py
```

Expected:

```text
ORKIO_RELEASE_0_5_0_REGRESSION_PASS
```
