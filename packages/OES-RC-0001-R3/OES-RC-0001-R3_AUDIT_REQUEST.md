# OES-RC-0001-R3 — Audit Request

Valdex, audit `OES-RC-0001-R3_ENGINEERING_FOUNDATION_REPO_READY.zip`.

## Context
This revision supersedes OES-RC-0001-R2 after a NO-GO caused by a P1 executable preflight defect: the Python validator contained an invalid backslash escape sequence and therefore could not run.

## Validate
1. All files are under `specification/`.
2. No root-level files exist.
3. Package control files are isolated under `specification/packages/OES-RC-0001-R3/`.
4. ZIP entries are inspected before extraction.
5. Unsafe paths are rejected before extraction.
6. Symlinks are rejected before extraction.
7. Empty path segments and current-directory segments are rejected before normalization.
8. The Python validator compiles before it gates extraction.
9. Normalized extraction destinations remain inside staging.
10. Duplicate normalized extraction destinations are rejected.
11. Manifest hashes match after extraction into temporary staging.
12. No absolute paths, traversal, cache, compiled files, symlinks, or source-code changes exist.
13. Approval authority is Vision Owner + Independent Engineering Auditor.
14. OES-001 through OES-004 are promoted atomically if approved.
15. ZIP SHA-256 evidence is recorded externally, not inside the ZIP.

## Expected Decision
GO if no P0/P1 findings remain.

## Out of Scope
Runtime, backend, frontend, deployment, database, API, agent behavior, and UI changes.
