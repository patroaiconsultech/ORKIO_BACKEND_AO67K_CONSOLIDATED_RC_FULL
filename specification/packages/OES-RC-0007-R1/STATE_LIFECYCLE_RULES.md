# State Lifecycle Rules

## Lifecycle Statuses

- `initialized`
- `active`
- `suspended`
- `archived`

## Rules

1. A state model starts as `initialized` only after an accepted command produces a primary event.
2. A state model becomes `active` when it is eligible for normal command processing.
3. A state model may become `suspended` only through a future approved policy boundary.
4. A state model may become `archived` only through a future approved retention boundary.
5. Rejected commands do not mutate canonical state.
6. Idempotent replay does not duplicate state writes.
