# Changelog — ORKIO CORE RC2 Runtime Foundation

## Consolidated from approved sequence

- EPIC-002A: Runtime Persistence Shadow baseline.
- EPIC-002B-R1: Canonical deterministic assistant message identity using JSON canonical serialization.
- EPIC-002C-R2: Target-only import hygiene in `runtime/intent_engine.py`.
- EPIC-002D-R1: Target-only core namespace normalization in `services/governance_service.py`.
- EPIC-002E-R2: Target-only services namespace normalization in `services/governance_service.py`.
- EPIC-002F-R1: Target-only core capability namespace normalization in `services/capability_service.py`.

## Removed from consolidation

- Obsolete EPIC-002 initial package.
- EPIC-002B non-R1 delimiter serialization.
- EPIC-002C original and R1 corrupt patch flow.
- EPIC-002E-R1 documentary mismatch.
- `__pycache__` and `.pyc`.

## RC2-R2 Hardening

- Removed `--skip-sha-check`; baseline SHA guard is mandatory.
- Added pre-write rejection for forbidden `app/config/runtime.py` shim path.
- Removed residual shim authorization from canonical persistence docs.
- Expanded SHA guard tests to cover absent bypass and pre-existing shim rejection.


## RC2-R2 Artifact Hygiene

- Removed `.pytest_cache/` from the release ZIP.
- Manifest regenerated after cache removal.
- Package validation must run pytest with `-p no:cacheprovider` to prevent cache mutation during audit.
