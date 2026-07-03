# Contract — EPIC-002F Core Capability Import Hygiene Target

## Authority

This EPIC does not create a new authority.

It only normalizes a legacy import path in one target file.

## Target

```text
services/capability_service.py
```

## Canonical import

```text
core.orkio_capabilities
```

## Legacy import

```text
app.core.orkio_capabilities
```

## Non-goals

- No shim.
- No fallback.
- No package alias.
- No Runtime Foundation change.
- No SSE change.
- No database change.
- No production behavior change.

## Acceptance

The target file must not reference `app.core.orkio_capabilities` after application.
The target file must reference `core.orkio_capabilities`.
The destination file `core/orkio_capabilities.py` must exist.
