# Repository Port Catalog

Repository ports are specification boundaries. They are not runtime implementations.

## Required Generic Operations

- `load_by_reference`
- `save_projection`
- `append_version`
- `check_version`
- `record_idempotency_result`
- `stage_outbox_event`
- `write_audit_record`

## Rules

- Future handlers must use repository ports instead of direct persistence calls.
- Repository ports must preserve correlation, causation, audit and idempotency references.
- Repository ports must not store raw founder private context.
