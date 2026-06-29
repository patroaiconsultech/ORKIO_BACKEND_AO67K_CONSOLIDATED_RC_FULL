# OEP-007 — Autonomous Planner Foundation

## Objective

Create the first governed planning layer for ORKIO.

The planner does not execute actions. It only creates proposal-only plans that require human approval.

## Scope

- `evolution/autonomous_planner/`
- `tests/oep007_autonomous_planner_foundation_smoke.py`

## Governance

Every plan and step must preserve:

- `proposal_only=True`
- `write_executed=False`
- `human_approval_required=True`

## Validation

```bash
PYTHONPATH=. python -m py_compile evolution/*.py evolution/autonomous_planner/*.py tests/oep007_autonomous_planner_foundation_smoke.py
PYTHONPATH=. python tests/oep007_autonomous_planner_foundation_smoke.py
```

Expected:

```txt
OEP007_AUTONOMOUS_PLANNER_FOUNDATION_PASS
```

## Regression

Run:

```bash
PYTHONPATH=. python tests/regression/run_regression_suite.py
```
