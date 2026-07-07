# Outbox, Inbox and Audit State Rules

## Outbox

Accepted commands stage exactly one primary success event through the future outbox boundary.

## Inbox

Future inbound integration messages must be deduplicated before state mutation.

## Audit State

Every accept/reject state decision must preserve:

- actor reference;
- command reference;
- event reference when applicable;
- correlation ID;
- causation ID;
- timestamp;
- normalized outcome.

No audit state may contain raw private founder content.
