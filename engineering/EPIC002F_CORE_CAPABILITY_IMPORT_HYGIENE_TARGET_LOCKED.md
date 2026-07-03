# EPIC-002F — Core Capability Import Hygiene Target Locked

## Objective

Resolve the next confirmed integrated import blocker:

```text
services.capability_service
    -> app.core.orkio_capabilities
    -> ModuleNotFoundError
```

## Patch type

Target-only import hygiene.

## Target

```text
services/capability_service.py
```

## Change

```text
app.core.orkio_capabilities -> core.orkio_capabilities
```

## Risk

Low in branch/shadow. No business logic is changed.

## Rollback

```bash
git checkout -- services/capability_service.py
```

## GO / NO-GO

GO for branch/shadow target-only.
NO-GO for production.
