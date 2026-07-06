# OES-RC-0003-R3 — Changelog

## R3

Patch scope restricted to the final OES-006 independent audit findings and release-readiness defects.

### Changed

- Closed the Produced References vocabulary against the canonical reference inventory.
- Normalized the four non-canonical Produced References reported by audit to approved canonical inventory entries.
- Updated `coverage_check.py` to fail when any Produced Reference is outside `vocabulary_inventory.json`.
- Updated `collision_check.py` to enforce explicit preimage allow-list replacement behavior.
- Updated package metadata, release notes, validation checklist and manifest for R3 consistency.

### Unchanged

- Capability IDs.
- Capability Names.
- Aggregate Roots.
- Authorities.
- Lifecycles.
- Applicable Aggregate Invariants.
- Canonical References.
- Contracts, Events and Runtime Projection identifiers.
- Runtime/backend code.
