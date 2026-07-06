# OES-RC-0003-R3 — Release Notes

OES-RC-0003-R3 is a restricted release-engineering patch over OES-RC-0003-R2.

The canonical capability nucleus remains unchanged. This release closes the Produced References vocabulary, adds permanent validation against the canonical reference inventory, aligns replacement/preimage policy, and refreshes package metadata and manifests for audit readiness.

## Scope

Included:

- `specification/OES-006_CAPABILITY_CATALOG.md`
- `specification/packages/OES-RC-0003-R3/`

Excluded:

- Runtime code.
- Backend/frontend behavior.
- API contracts beyond their catalog identifiers.
- OES-005 canonical model changes.
- New domain concepts.

## Audit Focus

Auditors should verify:

- 56/56 capabilities are preserved.
- No inherited canonical field changed.
- Produced References are contained in the canonical reference inventory.
- Collision/preimage policy is deterministic.
- Manifest hashes match package contents.
