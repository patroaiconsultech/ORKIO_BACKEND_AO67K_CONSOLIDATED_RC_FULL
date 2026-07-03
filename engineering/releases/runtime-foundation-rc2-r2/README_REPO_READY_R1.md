# ORKIO Backend Repo-Ready RC2-R2 R1

This artifact fixes the repo-ready layout mismatch found by AO-01.

## Critical operational rule

Extract/upload into the backend repository root, but do not commit before
running the applier.

The applier is locked to:

`94ba9246bcd3d2a5c40d42657ae7ca17c80a2826`

If you already committed the previous repo-ready upload, reset/revert and create
a fresh branch from the locked SHA before using this R1 package.

## Validation

```bash
git rev-parse HEAD
python tools/apply_shadow_candidate.py --check
python tools/apply_shadow_candidate.py --write
python tools/apply_shadow_candidate.py --write
python tools/validate_shadow_candidate.py
pytest -p no:cacheprovider tests/runtime tests/repository
python -c "import runtime.orkio_runtime_foundation.persistence; print('Runtime Foundation import: PASS')"
git diff -- main.py
```

Expected:
- SHA guard accepts only the locked baseline.
- No `payload/` lookup.
- Import hygiene applies to the three approved targets.
- `main.py` remains unchanged.
