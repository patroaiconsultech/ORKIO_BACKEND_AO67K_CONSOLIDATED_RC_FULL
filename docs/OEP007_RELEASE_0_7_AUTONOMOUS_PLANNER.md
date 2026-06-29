# OEP-007 Release 0.7.0 — Autonomous Planner Foundation

## Scope

This release expands the Autonomous Planner with governed planning capabilities:

- OEP-007: Autonomous Planner Foundation
- OEP-007.1: Planner Safety Gate
- OEP-007.2: Plan Risk Scoring
- OEP-007.3: Plan Dependency Graph
- OEP-007.4: Planner → Proposal Bridge
- OEP-007.5: Regression Suite v0.7.0

## Governance

All planner outputs must preserve:

- `proposal_only=True`
- `write_executed=False`
- `human_approval_required=True`

The planner is not an execution engine. It only produces structured plans and proposal packages for human review.

## Validation

Run:

```bash
PYTHONPATH=. python tests/regression/run_regression_suite.py
```

Expected:

```txt
ORKIO_RELEASE_0_7_0_REGRESSION_PASS
```
