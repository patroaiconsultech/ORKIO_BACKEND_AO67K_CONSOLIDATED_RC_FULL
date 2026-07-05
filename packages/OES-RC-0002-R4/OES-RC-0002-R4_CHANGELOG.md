# OES-RC-0002-R4 — Changelog

## 0.1-rc-r4

### Fixed P1 Findings

- Removed `__pycache__/` and Python bytecode from the package.
- Added mandatory package hygiene gate rejecting `__pycache__/`, `*.pyc`, and `*.pyo`.
- Regenerated manifest and package ZIP after hygiene cleanup.

### Editorial P2/P3

- Renamed `Target Aggregate` to `Target Concept` where references may target non-root concepts.
- Corrected package title/version metadata to R4.
- Declared package-local validation tooling as permitted specification tooling, not runtime source code.

## 0.1-rc-r3

### Fixed P1 Findings

- Removed unverifiable historical baseline SHA as a promoted dependency.
- Declared foundation applied commit as an external promotion gate.
- Separated Entities, Value Objects and References in every aggregate.
- Removed `ExecutionHistory` as an Agent-owned entity; execution history is represented by Observability references.
- Covered missing lifecycle transitions for Organization, Membership, Agent, Conversation and Policy.
- Qualified immutability as immutable business/evidential content plus authorized lifecycle metadata transitions.
- Added executable collision check to preflight.
- Added coverage sanity test for state machine and metamodel consistency.

### Premium Hardening

- Added complete state machine coverage matrix.
- Added complete capability matrix.
- Added complete derivation matrix.
- Added ownership matrix with reference semantics.
- Added package-local `coverage_check.py` and `collision_check.py`.

## 0.1-rc-r1

- Added evidence taxonomy, metadata alignment, capability semantics and premium matrices.

## 0.1-rc

- Initial Canonical Domain Model release candidate.
