# ADR-0007 — Core Capability Import Hygiene Target Only

## Status

Accepted for SHADOW audit.

## Context

After EPIC-002E, integrated import advanced to:

```text
services.capability_service -> app.core.orkio_capabilities
```

The baseline contains the canonical module under:

```text
core/orkio_capabilities.py
```

## Decision

Normalize only the target import in `services/capability_service.py`.

## Consequences

The import chain advances without introducing shims or fallback behavior.
Any next blocker must be handled in a separate EPIC.
