# Private Context Triage Layer

Release Candidate: OES-RC-0005-R4

## Definition

The Private Context Triage Layer is the mandatory boundary between private founder sources and any ORKIO usage.

## Enforcement Principles

1. Deny by default.
2. Metadata-only registration before content access.
3. No raw content in public repositories.
4. No source candidate usage without founder approval.
5. No runtime memory from private content without a future approved implementation gate.
6. No learning from sensitive content; only sanitized learning signals are allowed.

## State Machine

```text
PRIVATE_SOURCE_CANDIDATE
        ↓
REGISTERED_METADATA_ONLY
        ↓
CLASSIFIED
        ↓
SANITIZED_OR_MINIMIZED
        ↓
AUTHORIZED
        ↓
APPROVED_CONTEXT_ARTIFACT
        ↓
PURPOSE_BOUND_USAGE
```

A source may also transition to:

```text
QUARANTINED
DO_NOT_USE
```

## Current Registered Source Candidates

The current package registers source candidates only by metadata. No source content is included, opened, linked or quoted.
