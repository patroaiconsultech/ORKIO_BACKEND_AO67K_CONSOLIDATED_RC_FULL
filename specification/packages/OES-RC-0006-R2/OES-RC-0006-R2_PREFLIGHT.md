# OES-RC-0006-R2 Preflight

## Baseline

- OES-007 document SHA-256: `C67F471AAA59D0EAF57F791ED43679D0714D990903CC927A4FAE18DCD8A88B26`
- OES-008 document SHA-256: `7C316C9D218E111CD486A9E40BFD48A3E0C61B859B3D0E9F6D6C2AFBDB9552CD`

## Expected Scope

- Add `specification/OES-009_HANDLER_BOUNDARY_RUNTIME_MAPPING.md`
- Add `specification/packages/OES-RC-0006-R2/`
- No runtime/API/database/infrastructure changes

## Required Checks

- `manifest_check.py`
- `scope_check.py`
- `coverage_check.py`
- `boundary_consistency_check.py`
- `vocabulary_closure_check.py`
- `privacy_boundary_check.py`
- `collision_check.py <baseline_repo_dir>`
