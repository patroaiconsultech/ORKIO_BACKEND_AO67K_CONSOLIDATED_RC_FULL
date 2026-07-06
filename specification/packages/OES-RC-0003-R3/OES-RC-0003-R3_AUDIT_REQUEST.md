# Audit Request — OES-RC-0003-R3

## Objective

Audit OES-RC-0003-R3 as a restricted final patch over OES-RC-0003-R2 for OES-006 baseline readiness.

## Requested Focus

Please verify:

1. OES-006 preserves the OES-005/R4 canonical capability nucleus.
2. All 56 expected capabilities are present.
3. No capability IDs, names, aggregate roots, authorities, lifecycles, applicable invariants or canonical references were changed.
4. Produced References are fully contained in the canonical reference inventory.
5. `coverage_check.py` fails on Produced References outside the inventory.
6. `collision_check.py` allows only declared preimage replacements.
7. Manifest hashes match the package contents.
8. No runtime/backend/frontend code is included.

## Expected Result

GO if no divergence, vocabulary, manifest, collision or package hygiene issue is found.
