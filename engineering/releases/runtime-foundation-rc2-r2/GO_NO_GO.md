# GO / NO-GO — ORKIO CORE RC2 Runtime Foundation

## GO

- Apply to branch/shadow for independent audit.
- Execute full validation checklist.
- Use as candidate baseline for future SHADOW → GUARDED review.

## NO-GO

- No production deployment.
- No enforcement.
- No guarded promotion without independent audit.
- No application over a different baseline SHA.

## Artifact hygiene

- `.pytest_cache/`, `__pycache__`, `.pyc`, and `.pyo` are forbidden in the release ZIP.
