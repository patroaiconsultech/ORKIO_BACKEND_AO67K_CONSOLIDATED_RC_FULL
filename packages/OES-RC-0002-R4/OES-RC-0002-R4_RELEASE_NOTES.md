# OES-RC-0002-R4 — Release Notes

OES-RC-0002-R4 is a corrective release candidate for the Canonical Domain Model.

It resolves R1 P1 findings related to baseline evidence, metamodel classification, Evidence ownership, ExecutionHistory ownership, lifecycle coverage, immutability semantics and executable preflight collision checks.

No runtime, backend, frontend, infrastructure, deployment configuration, cache, compiled artifact or source code is modified.

## R4 Notes

R4 applies a small semantic closure patch:

- all named cross-aggregate references are now present in the Canonical Concept Inventory;
- references have stable IDs, type `Reference`, target aggregate and owning authority;
- implicit aliases are prohibited;
- coverage tooling now fails when aggregate specifications use concepts not present exactly once in the inventory.

## R4 Hygiene Update

R4 removes cache/compiled artifacts and adds a mandatory package hygiene gate for `__pycache__/`, `*.pyc`, and `*.pyo`.
