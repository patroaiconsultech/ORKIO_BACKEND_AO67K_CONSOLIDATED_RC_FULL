# OES-RC-0004-R1 — Idempotency and Traceability Rules

## Idempotency

Every command contract MUST include `idempotency_key`.

The key scope is:

```text
capability_id + aggregate_reference + actor_agent_reference + request_intent
```

If an identical command is received with the same key, the system SHOULD return the previously accepted outcome.

If a conflicting command is received with the same key, the system MUST reject it and register an audit record.

## Causation

Every command and every domain event MUST include `causation_id`.

The first command in a workflow MAY set `causation_id` equal to its own `message_id`.

Derived commands/events MUST preserve causation back to the triggering message.

## Correlation

Every command and every event MUST include `correlation_id`.

A workflow MUST preserve the same `correlation_id` across related commands, events, audit records and later runtime projections.

## Auditability

Every success event MUST be eligible for `AuditRecordReference` correlation.

Rejected commands MUST NOT emit primary success events, but MUST remain audit-recordable.

## Runtime Boundary

This document defines normative message semantics only. It does not implement runtime dispatch, queues, persistence, replay or external APIs.
