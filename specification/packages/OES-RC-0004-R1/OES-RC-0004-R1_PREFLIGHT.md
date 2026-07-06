# OES-RC-0004-R1 — Preflight

## Baseline

- Baseline source: ORKIO backend with OES-006 RC-0003-R3 applied
- OES-006 SHA-256: `C17580C10C773B5D7917D35DE6A90C62919CA14A2670E4222AE971492CC3FC64`

## Expected Result

- Add OES-007 specification document.
- Add OES-RC-0004-R1 audit package.
- Keep all changes under `/specification`.
- Avoid runtime, API, database and infrastructure changes.

## Required Local Commands

```bash
python specification/packages/OES-RC-0004-R1/coverage_check.py
python specification/packages/OES-RC-0004-R1/vocabulary_closure_check.py
python specification/packages/OES-RC-0004-R1/manifest_check.py
python specification/packages/OES-RC-0004-R1/collision_check.py .
```

## Gate

Promotion requires all checks to pass and independent READONLY_AUDIT approval.
