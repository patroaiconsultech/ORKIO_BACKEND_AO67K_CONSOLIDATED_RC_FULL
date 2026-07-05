# Coverage Tests

## Purpose

Define executable coverage checks required before submitting this package to independent audit.

## Required Checks

- Every declared lifecycle target state has a contract and event in `STATE_MACHINE_MATRIX.md`.
- Every state-changing capability appears in `CAPABILITY_MATRIX.md`.
- Every state-changing contract appears in `DERIVATION_MATRIX.md`.
- No concept appears both as Entity and Value Object in OES-005.
- No reference is classified as owned Entity.
- Collision check is executable in preflight.

## Python Sanity Test

The following check is intentionally simple and package-local.

```bash
python specification/packages/OES-RC-0002-R4/coverage_check.py
```

Expected result:

```text
COVERAGE CHECK PASS
```

## R3 Coverage Extension

The R3 coverage gate adds vocabulary closure checks:

- every concept listed in `Entities:` must exist exactly once in the Canonical Concept Inventory;
- every concept listed in `Value Objects:` must exist exactly once in the Canonical Concept Inventory;
- every concept listed in `References:` must exist exactly once in the Canonical Concept Inventory with type `Reference`;
- duplicate Domain IDs are rejected;
- duplicate concept names are rejected;
- implicit aliases are rejected.
