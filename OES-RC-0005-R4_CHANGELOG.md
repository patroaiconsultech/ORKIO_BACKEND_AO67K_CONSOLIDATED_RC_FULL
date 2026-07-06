# OES-RC-0005-R4 Changelog

## Type

Patch minimum after READONLY_AUDIT YELLOW on OES-RC-0005-R1.

## Changes

* Corrected custody language by separating OES-007 document SHA from OES-007 backend ZIP SHA.
* Changed partial private source current use to `metadata_only_without_content_access`.
* Added explicit `content_access_allowed: false` for source candidates.
* Added safe Learning Signals Policy.
* Strengthened privacy boundary checker to inspect Markdown, JSON, YAML, TXT and Python files.
* Closed the source-candidate schema with `additionalProperties: false`.
* Fixed source candidate publication and approval constraints.
* Replaced nominal collision check with a baseline-aware collision check.
* Updated package metadata and audit request for R4.

## Non-changes

* No runtime code changed.
* No API changed.
* No database changed.
* No infrastructure changed.
* No private source content included.


## R3 procedural hardening

* Regenerated the added-files diff as a valid unified diff with proper hunk/header line breaks.
* Hardened `collision_check.py` to authenticate the declared OES-007 baseline by checking `specification/OES-007_CONTRACT_EVENT_PROJECTION.md` SHA-256.
* Added explicit failure if the expected OES-RC-0004-R1 package is absent from the baseline.
* Added explicit failure if the target baseline already contains OES-008/R4 paths.
* No policy, privacy, runtime, API, database or infrastructure behavior was changed.


## R4 tooling and custody hardening

* Normalized validator path comparisons with `Path.as_posix()` so checks are reproducible on Windows and POSIX environments.
* Updated `manifest_check.py`, `scope_check.py`, and `collision_check.py` to avoid false failures caused by `\` path separators.
* Preserved baseline authentication in `collision_check.py` through the OES-007 document SHA-256.
* Regenerated the standalone backend-applied ZIP without embedding any handoff ZIP or audit bundle inside it.
* Regenerated manifest, SHA256SUMS, build report, handoff and repo-ready package.
* No policy, privacy, runtime, API, database or infrastructure behavior was changed.
