# ORKIO Emergency Backend Restore — AO-01

## Root cause

`main.py` is imported as `app.main` and contains:

```python
from .agent_evolution_map.router import (
    AgentEvolutionMapRouterDeps,
    build_agent_evolution_map_router,
)
```

Therefore Python expects this package at:

```text
<repo-root>/agent_evolution_map/
```

The current source package exists at:

```text
<repo-root>/app/agent_evolution_map/
```

Inside the container that becomes `/app/app/agent_evolution_map`, while the import expects
`/app/agent_evolution_map`.

## Emergency patch

Overlay the folder `agent_evolution_map/` from this pack into the repository root.

Final structure:

```text
main.py
__init__.py
agent_evolution_map/
  __init__.py
  router.py
  service.py
  contracts.py
  adapters.py
```

Do not alter SSE, OCIL, upload, database or frontend.

## Validation before deploy

```bash
test -f agent_evolution_map/router.py
python -m compileall -q agent_evolution_map
PYTHONPATH="$(pwd)/.." python -c "import app.agent_evolution_map.router; print('AGENT_EVOLUTION_MAP_IMPORT_OK')"
PYTHONPATH="$(pwd)/.." python -c "import app.main; print('ORKIO_MAIN_IMPORT_OK')"
```

## Deploy

Perform a clean rebuild with cache invalidation.

## Rollback

Rollback to the last healthy deployment if either import smoke test fails.
