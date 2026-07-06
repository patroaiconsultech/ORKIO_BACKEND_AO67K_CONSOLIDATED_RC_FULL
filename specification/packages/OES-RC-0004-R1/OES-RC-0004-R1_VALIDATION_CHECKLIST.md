# OES-RC-0004-R1 — Validation Checklist

## Package Integrity

- [ ] ZIP opens successfully.
- [ ] No path traversal.
- [ ] No symlinks.
- [ ] No cache, `.pyc`, `.pyo`, build or temporary files.
- [ ] Manifest hashes match package contents.

## Coverage

- [ ] 56 capabilities projected.
- [ ] 56 unique command contracts.
- [ ] 56 unique primary events.
- [ ] Every command links to one OES-006 capability.
- [ ] Every event links to one OES-006 capability.

## Vocabulary

- [ ] Reference vocabulary is inherited from OES-006.
- [ ] Zero references outside vocabulary.
- [ ] Zero forbidden non-canonical references:
  - `MembershipReference`
  - `CapabilityBindingReference`
  - `DelegationReference`
  - `CorrelationReference`

## Scope

- [ ] Only `/specification` files are added.
- [ ] No runtime changes.
- [ ] No API changes.
- [ ] No database changes.
- [ ] No infrastructure changes.

## Decision

- [ ] GREEN — safe for merge/manual upload.
- [ ] YELLOW — apply only with stated mitigations.
- [ ] RED — do not apply.
