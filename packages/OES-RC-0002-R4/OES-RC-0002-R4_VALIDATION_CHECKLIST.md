# OES-RC-0002-R4 — Validation Checklist

## Package Integrity

- [ ] All files are under `specification/`.
- [ ] No root-level files are created.
- [ ] Manifest validates.
- [ ] Pre-extraction validation passes.
- [ ] No unsafe path, symlink or non-regular file exists.
- [ ] Collision check is executed against target repository before promotion.

## Domain Consistency

- [ ] Entities, Value Objects and References are separated.
- [ ] No concept is classified in contradictory categories.
- [ ] No aggregate owns entities belonging to another authority.
- [ ] Evidence taxonomy is unambiguous.
- [ ] ExecutionHistory ownership conflict is removed.

## Lifecycle Coverage

- [ ] Every lifecycle state has a capability, contract and event.
- [ ] Decision Rejected behavior is explicit.
- [ ] Policy Superseded is covered.
- [ ] Conversation Paused and Resumed are covered.
- [ ] Organization Suspended and Archived are covered.
- [ ] Agent Archived is covered.

## Promotion Gates

- [ ] OES-RC-0001-R3 has Vision Owner approval.
- [ ] OES-RC-0001-R3 has been applied to target repository.
- [ ] Resulting foundation-applied commit SHA is externally recorded.
- [ ] This package preflight is executed against that repository state.

## Evidence

- Executor:
- Date:
- Target Repository:
- Foundation Applied Commit SHA:
- This Package SHA-256:
- Result:
