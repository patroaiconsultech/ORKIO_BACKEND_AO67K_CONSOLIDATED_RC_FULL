# OES-RC-0001-R3 — Changelog

## 0.1-rc-r3
- Corrects the executable Python preflight validator escape sequence for backslash detection.
- Requires the Python validator to compile with `python3 -m py_compile` before it can gate extraction.
- Rejects empty ZIP path segments and current-directory segments before normalization.
- Rejects duplicate normalized extraction destinations, including case-folded destination collisions.
- Applies premium destination hardening by resolving each destination with `strict=False` and confirming it remains inside staging.
- Preserves pre-extraction ZIP entry inspection, `grep -E` traversal checks, symlink rejection, external ZIP SHA attestation, and atomic promotion rules.

## 0.1-rc-r2
- Added mandatory pre-extraction ZIP entry inspection before `unzip`.
- Corrected regex usage with `grep -E` for alternation and traversal checks.
- Added normalized path destination validation to ensure extraction remains inside staging.
- Added explicit symlink rejection before extraction.
- Moved ZIP SHA-256 recording to external audit/PR/commit attestation to avoid self-referential hash cycles.
- Aligned document headers to `Version: 0.1-rc-r2`.

## 0.1-rc-r1
- Corrected preflight procedure to extract into an isolated temporary staging directory before validating manifest hashes.
- Standardized approval authority as Vision Owner + Independent Engineering Auditor.
- Defined rejection flow and repository promotion responsibility.
- Declared atomic baseline promotion for OES-001 through OES-004.
- Added execution evidence fields to validation checklist.

## 0.1-rc
- Introduced Orkio Engineering Specification foundation package.
