# OES-RC-0001-R3 — Release Notes

## Summary
Revision R3 of the Orkio Engineering Foundation release candidate.

## Changes Since OES-RC-0001-R2
- Corrected the Python preflight validator syntax so the gate is executable.
- Added mandatory `python3 -m py_compile` validation for the generated validator before extraction.
- Added rejection of empty ZIP path segments and current-directory path segments before normalization.
- Added rejection of duplicate normalized extraction destinations.
- Added premium destination hardening using resolved paths to confirm every destination remains inside staging.

## Preserved From Earlier Revisions
- ZIP entries are inspected before extraction.
- Unsafe paths and symlinks are rejected before extraction.
- Manifest hashes are verified only after extraction into isolated staging.
- ZIP SHA-256 evidence is recorded externally, not inside the ZIP.
- OES-001 through OES-004 are promoted atomically if approved.

## Intended Use
Submit to independent audit. If approved, promote OES-001 through OES-004 atomically to Engineering Baseline v1.0.

## Not Intended For
This package is not a runtime, backend, frontend, infrastructure, database, or deployment patch.
