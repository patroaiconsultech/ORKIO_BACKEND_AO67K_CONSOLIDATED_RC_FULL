# ORKIO AO-01 Emergency Boot Hotfix

## Objective
Prevent `app.agent_evolution_map` from crashing the entire backend during import.

## Exact changes
1. Wraps the import of `.agent_evolution_map.router` in a fail-open guard.
2. Registers the router only when the module loaded successfully.
3. Emits one of:
   - `AGENT_EVOLUTION_MAP_ROUTER_BOOT_OK`
   - `AGENT_EVOLUTION_MAP_ROUTER_DISABLED`

## Apply
Replace the deployed `main.py` with the included `main.py`.

## Mandatory validation
```bash
python -m py_compile main.py
python -c "import main; print('ORKIO_MAIN_IMPORT_OK')"
```

Expected when the optional package is absent:
```text
AGENT_EVOLUTION_MAP_ROUTER_DISABLED ...
ORKIO_MAIN_IMPORT_OK
```

Expected when the package is present:
```text
AGENT_EVOLUTION_MAP_ROUTER_BOOT_OK
ORKIO_MAIN_IMPORT_OK
```

## Scope
No changes to:
- database
- Alembic
- SSE
- upload
- OCIL
- frontend
- authentication

## Rollback
Restore the previous `main.py` or rollback the deployment.
