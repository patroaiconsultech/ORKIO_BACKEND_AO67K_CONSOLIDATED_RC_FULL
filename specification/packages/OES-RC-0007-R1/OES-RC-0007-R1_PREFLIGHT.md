# OES-RC-0007-R1 Preflight

## Baseline

- OES-007 SHA-256: `C67F471AAA59D0EAF57F791ED43679D0714D990903CC927A4FAE18DCD8A88B26`
- OES-008 SHA-256: `7C316C9D218E111CD486A9E40BFD48A3E0C61B859B3D0E9F6D6C2AFBDB9552CD`
- OES-009 handler mapping SHA-256: `DD8FCDA6426516E6AE014B97CC127A07F86B4D37CD025A4F97E4752D8AFF60BD`

## Expected Scope

- Add `specification/OES-010_PERSISTENCE_AND_STATE_MODEL.md`
- Add `specification/packages/OES-RC-0007-R1/`
- No runtime/API/database/infrastructure changes

## Required Checks

- `manifest_check.py`
- `scope_check.py`
- `coverage_check.py`
- `state_consistency_check.py`
- `vocabulary_closure_check.py`
- `privacy_boundary_check.py`
- `collision_check.py <baseline_repo_dir>`
