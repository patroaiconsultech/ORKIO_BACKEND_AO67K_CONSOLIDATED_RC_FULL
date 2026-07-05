# OES-004 — Engineering Delivery Standard

Version: 0.1-rc-r3
Status: RELEASE CANDIDATE
Owner: Orkio Engineering Office
Approver: Vision Owner + Independent Engineering Auditor
Depends on: OES-001, OES-002, OES-003

## Objective
Define the standard for packaging, validating, auditing, and delivering Orkio engineering artifacts.

## Scope
Applies to every OES release candidate and future specification package.

## Out of Scope
Runtime implementation, deployment automation, and CI/CD provider configuration.

## Directory Rules
- All package content must be relative to repository root.
- All specification content must remain under `specification/`.
- No file may be created at repository root unless explicitly approved.
- Package control files must live under `specification/packages/<package-id>/`.
- Package control file names must include the package ID.

## Required Package Control Files
- `<package-id>_PACKAGE_METADATA.md`
- `<package-id>_MANIFEST_SHA256.txt`
- `<package-id>_CHANGELOG.md`
- `<package-id>_VALIDATION_CHECKLIST.md`
- `<package-id>_PREFLIGHT.md`
- `<package-id>_AUDIT_REQUEST.md`
- `<package-id>_RELEASE_NOTES.md`

## Manifest Rules
- SHA-256 is required.
- Manifest lists every file except itself.
- Paths are repository-relative.
- Paths must not contain absolute paths or `..`.

## Preflight Rules
1. Inspect ZIP entries before extraction using the ZIP central directory.
2. Reject any entry that is not under `specification/`.
3. Reject absolute paths, Windows drive paths, path traversal, empty path segments, and backslash traversal.
4. Reject symlinks and non-regular file entries unless explicitly approved by a future package standard.
5. Normalize every ZIP entry path and confirm the resolved extraction destination remains inside the temporary staging directory.
6. Only after pre-extraction validation passes, extract the package into a temporary staging directory outside the target repository.
7. Validate SHA-256 manifest inside the staging directory.
8. Compare staged paths with target repository paths.
9. Block unexpected collisions before copying anything into the repository.
10. Allow intentional updates only when declared in metadata.
11. Confirm no root-level files are present.
12. Copy into the target repository only after staging validation passes.

## Collision Policy
A package is non-destructive only when it creates new files or updates files explicitly listed as intended replacements.

## Document Template
Every normative OES document must include title, version, status, owner, approver, dependencies, objective, scope, out of scope, acceptance criteria, risks, next steps, and revision history.

## Acceptance Criteria
- Package structure prevents metadata collisions.
- Preflight can be executed manually.
- Metadata declares target repository and collision policy.
- Manifest validates all included files.

## Risks
- Manual preflight may be skipped unless enforced by process.

## Next Steps
Apply this standard to all future packages.

## Revision History
- 0.1-rc: Initial release candidate.
- 0.1-rc-r1: Corrected preflight order to use isolated staging before repository copy.
- 0.1-rc-r3: Standardized approval authority with OES-003.
