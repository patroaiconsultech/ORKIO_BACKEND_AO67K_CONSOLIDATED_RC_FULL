# OES-RC-0001-R3 — Validation Checklist

## Execution Record
- Date:
- Executor:
- Result: PASS / FAIL
- Evidence Location:
- External ZIP SHA-256 Attestation Location:
- Target Repository:
- Repository Baseline SHA:
- Auditor:
- Auditor Verdict:

## Structure
- [ ] All files are under `specification/`.
- [ ] No files exist at repository root.
- [ ] Package control files are under `specification/packages/OES-RC-0001-R3/`.
- [ ] Package control files include the package ID.

## Pre-Extraction Safety
- [ ] ZIP entries enumerated before extraction.
- [ ] Every ZIP entry starts with `specification/`.
- [ ] No absolute paths.
- [ ] No Windows drive paths.
- [ ] No path traversal.
- [ ] No backslash traversal.
- [ ] No empty path segments.
- [ ] No current-directory path segments.
- [ ] No symlinks.
- [ ] Python validator compiles before extraction.
- [ ] Normalized extraction destinations remain inside staging.
- [ ] Duplicate normalized extraction destinations are rejected.

## Staging Safety
- [ ] Package extracted into temporary staging outside the target repository after pre-extraction checks.
- [ ] No root-level files.
- [ ] No cache files.
- [ ] No compiled files.
- [ ] No runtime/backend/frontend code changes.
- [ ] Collision check executed before repository copy.

## Integrity
- [ ] Manifest exists.
- [ ] Manifest uses SHA-256.
- [ ] Manifest excludes itself.
- [ ] Manifest hashes match staged package contents.
- [ ] ZIP SHA-256 recorded externally, not inside the ZIP.

## Governance
- [ ] Approval authority uses Vision Owner + Independent Engineering Auditor.
- [ ] Atomic baseline promotion is declared for OES-001 through OES-004.
- [ ] Rejection and return-to-review flow is defined.

## Audit Gate
- [ ] No P0 findings.
- [ ] No P1 findings.
- [ ] P2 findings remediated or formally accepted with rationale.
