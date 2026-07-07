# OES-010 — Persistence and State Model

**Title:** Persistence and State Model
**Version:** 0.1-rc-r1
**Status:** Release Candidate
**Owner:** Chief Architecture & Engineering Officer (AO-01)
**Approver:** Vision Owner + Independent Engineering Auditor
**Release Candidate:** OES-RC-0007-R1

## Dependencies

- OES-006 — Capability Catalog (Baseline / OES-RC-0003-R3)
- OES-007 — Contract and Event Projection (Baseline / OES-RC-0004-R1)
- OES-008 — Founder Context Triage & Usage Governance (Baseline / OES-RC-0005-R4)
- OES-009 — Handler Boundary and Runtime Mapping (Baseline / OES-RC-0006-R2)
- OES-007 document SHA-256: `C67F471AAA59D0EAF57F791ED43679D0714D990903CC927A4FAE18DCD8A88B26`
- OES-008 document SHA-256: `7C316C9D218E111CD486A9E40BFD48A3E0C61B859B3D0E9F6D6C2AFBDB9552CD`
- OES-009 handler boundary mapping SHA-256: `DD8FCDA6426516E6AE014B97CC127A07F86B4D37CD025A4F97E4752D8AFF60BD`

## Objective

Define the normative persistence and state model for the 56 handler boundaries approved in OES-009.

OES-010 maps each handler boundary to one canonical aggregate state model, one repository port boundary and one state lifecycle policy for future implementation.

## Scope

This release candidate is **specification-only**.

It defines:

1. canonical aggregate state records;
2. repository port boundaries;
3. state lifecycle rules;
4. snapshot and replay rules;
5. outbox, audit and idempotency state rules;
6. retention and privacy state constraints;
7. baseline collision and scope checks for future implementation.

## Non-goals

- Do not create database migrations.
- Do not create tables, collections, indexes or schemas in runtime.
- Do not implement repositories.
- Do not write adapters.
- Do not create queues, workers or event stores.
- Do not expose API endpoints.
- Do not ingest private founder context.
- Do not store raw private content.

## Core Rule

Every OES-009 handler boundary maps to exactly one OES-010 state model.

```text
Handler Boundary
        ↓
Repository Port
        ↓
Canonical Aggregate State
        ↓
Outbox / Audit / Idempotency State
        ↓
Future Persistence Adapter
```

## Coverage

| Item | Count |
|---|---:|
| OES-009 handler boundaries | 56 |
| OES-010 state models | 56 |
| State repository groups | 8 |
| Runtime/API/DB/infra changes | 0 |

## State Rules

| Rule | Requirement |
|---|---|
| One state model per handler | Each handler boundary MUST map to exactly one canonical state model. |
| No direct persistence | Future handlers MUST persist through declared repository ports. |
| Event projection | Accepted commands MAY project state only through approved state models. |
| Rejection boundary | Rejected commands MUST NOT mutate canonical aggregate state. |
| Auditability | State mutations MUST preserve audit and trace references. |
| Idempotency | Idempotent replay MUST NOT duplicate writes. |
| Privacy boundary | State models MUST NOT store raw founder private content. |
| Runtime isolation | This RC MUST remain specification-only. |

## Privacy and Learning Boundary

OES-010 inherits OES-008 and OES-009.

The system may learn from persistence failures, replay outcomes and audit results only through sanitized operational signals.

State models MUST NOT store, index, emit, replay or learn from raw private source content.

## Release Candidate

The detailed machine-readable state model is in:

```text
specification/packages/OES-RC-0007-R1/persistence_state_model.json
```

The upload package is delta-only and contains only files introduced by OES-010 / OES-RC-0007-R1.
