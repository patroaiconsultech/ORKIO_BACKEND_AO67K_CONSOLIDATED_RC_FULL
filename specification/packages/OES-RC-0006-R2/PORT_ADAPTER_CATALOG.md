# Port and Adapter Catalog

This catalog is normative for future implementation but does not implement runtime behavior.

## Required Ports

- `CommandDispatchPort`
- `PolicyDecisionPort`
- `IdempotencyStorePort`
- `ReferenceResolutionPort`
- `AggregateRepositoryPort`
- `EventOutboxPort`
- `AuditRecordPort`
- `ClockPort`
- `TraceContextPort`

## Allowed Adapters

- `InboundCommandAdapter`
- `PolicyDecisionAdapter`
- `IdempotencyStoreAdapter`
- `ReferenceResolverAdapter`
- `AggregateRepositoryAdapter`
- `EventOutboxAdapter`
- `AuditRecordAdapter`
- `ClockAdapter`
- `TraceContextAdapter`

## Rule

Handlers may not directly perform persistence, event emission, audit writes, external calls or private context access. All side effects must pass through declared ports and future approved adapters.
