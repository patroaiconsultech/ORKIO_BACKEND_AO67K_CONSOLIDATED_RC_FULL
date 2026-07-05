# OES-RC-0002-R4 — Package Metadata

## Package Identity

- Package ID: `OES-RC-0002-R4`
- Package Title: Canonical Domain Model R4
- Package Version: `0.1-rc-r4`
- Status: Release Candidate
- Owner: Chief Architecture & Engineering Officer (AO-01)
- Approver: Vision Owner + Independent Engineering Auditor
- Generated At: `2026-07-05T00:00:00Z`

## Target Repository

- Repository: `patroaiconsultech/ORKIO_BACKEND_AO67K_CONSOLIDATED_RC_FULL`
- Target Path: `specification/`
- Read-only Repository HEAD from latest independent audit: `f9b083e76c4016f328b0c90abbeee37e76a9409e`
- Foundation Applied Commit SHA: `PENDING_EXTERNAL_PROMOTION_EVIDENCE`
- Required Foundation Package: `OES-RC-0001-R3`
- Required Foundation Package SHA-256: `8EBF8749AB64896C1E53A5F8EDB4F1D5BB50E78B5111A2BA138A6D4F1A11AB00`

## Dependency Evidence

This package depends on OES-001 through OES-004 as the Engineering Foundation.

Promotion to Baseline requires external evidence that OES-RC-0001-R3 has been approved by the Vision Owner and applied to the repository.

The commit SHA produced by that application must be recorded outside this ZIP before baseline promotion.

## Collision Policy

This package is non-destructive.

Allowed:

- creation of new files under `specification/OES-005_CANONICAL_DOMAIN_MODEL.md`;
- creation of new files under `specification/packages/OES-RC-0002-R4/`.

Blocked:

- root-level file creation;
- deletion of existing files;
- replacement of existing files unless explicitly declared;
- writes outside `specification/`;
- overwrites outside this package ID.

## Intentional Replacements

None.

## Non-Destructive Statement

The package introduces OES-005 and package-scoped auxiliary files only.

It shall not modify runtime, backend, frontend, infrastructure, deployment configuration, cache, compiled artifacts or source code.

## Package Files

This package is self-contained under `specification/` and package controls are isolated under `specification/packages/OES-RC-0002-R4/`.

r3_patch_focus:
  - canonical reference vocabulary closure
  - stable IDs for cross-aggregate references
  - coverage check reinforcement

## Package Content Policy

Runtime source code, cache and compiled artifacts are prohibited. Package-local validation tooling is permitted only when it supports preflight, coverage or collision checks and is not runtime/backend/frontend source code.
