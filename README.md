# ORKIO AO-01 Premium Runtime Patch — PROPOSAL_ONLY

## Scope
- preserves the prior `agent_evolution_map` fail-open boot guard
- centralizes OCIL environment parsing and validation
- introduces explicit `ACCESS_MODE`
- logs release identity and SHA-256 of the running `main.py`
- adds unit tests for safe and contradictory flag combinations

## Recommended environment

```text
ACCESS_MODE=open
OCIL_ENABLED=false
OCIL_SHADOW_MODE=true
OCIL_ATTACHMENT_ENFORCEMENT=false
OCIL_EXECUTION_ENFORCEMENT=false
```

Do not include literal quote characters in the platform value fields.

## Files
Copy into the same application package that contains `main.py`:

```text
main.py
runtime/__init__.py
runtime/ocil_config.py
runtime/access_mode.py
runtime/release_identity.py
tests/test_runtime_config.py
```

## Pre-deploy validation

```bash
python -m py_compile main.py
python -m py_compile runtime/ocil_config.py
python -m py_compile runtime/access_mode.py
python -m py_compile runtime/release_identity.py
python -m unittest tests/test_runtime_config.py
python -c "import main; print('ORKIO_MAIN_IMPORT_OK')"
```

## Expected boot evidence

```text
ORKIO_BOOT_IDENTITY ...
ORKIO_OCIL_CONFIG enabled=False shadow_mode=True ...
ORKIO_ACCESS_CONFIG mode=open ...
ORKIO_ACCESS_MODE_OPEN ...
AGENT_EVOLUTION_MAP_ROUTER_DISABLED ...
```

## GO gate
- no restart loop
- healthcheck 200
- no fatal `ModuleNotFoundError`
- exact `main_sha256` matches `MANIFEST.json`
- registration succeeds without special code only when `ACCESS_MODE=open`

## Rollback
Restore the previous files and set:

```text
ACCESS_MODE=invite_only
OCIL_ENABLED=false
OCIL_SHADOW_MODE=true
OCIL_ATTACHMENT_ENFORCEMENT=false
OCIL_EXECUTION_ENFORCEMENT=false
```
