# Handler Preconditions and Postconditions

## Preconditions

1. Command envelope validates against OES-007.
2. Command capability ID matches the handler capability ID.
3. The idempotency key is present and scoped correctly.
4. The actor resolves as `AgentReference`.
5. Policy decision authorizes the actor, capability and target aggregate.
6. Reference fields are within the closed vocabulary.
7. Private founder context is not accessed unless a future OES-008-approved context artifact exists.

## Postconditions

1. Accepted commands stage exactly one primary success event in the outbox.
2. Rejected commands emit no primary success event.
3. Accept/reject outcome is audit-recorded.
4. Correlation and causation IDs are preserved.
5. No raw private context is emitted, persisted or learned.
