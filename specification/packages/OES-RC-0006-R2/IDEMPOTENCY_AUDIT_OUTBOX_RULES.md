# Idempotency, Audit and Outbox Rules

## Idempotency

Handlers must treat the OES-007 `idempotency_key` as mandatory. Duplicate semantic requests should return the previously accepted result. Conflicting duplicates must be rejected.

## Audit

Every accepted or rejected command must be audit-recorded through `AuditRecordPort`.

## Event Outbox

Accepted commands must stage the primary success event through `EventOutboxPort`. The handler boundary does not publish directly to infrastructure.

## Failure Policy

Failures and rejections are not domain success events. They must be normalized, audit-recorded and returned without private or sensitive leakage.
