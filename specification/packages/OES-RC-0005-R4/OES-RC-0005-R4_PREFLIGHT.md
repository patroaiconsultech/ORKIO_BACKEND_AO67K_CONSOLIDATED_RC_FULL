# OES-RC-0005-R4 Preflight

## Required Commands

From the repository root after applying the package:

```bash
python specification/packages/OES-RC-0005-R4/manifest_check.py
python specification/packages/OES-RC-0005-R4/classification_check.py
python specification/packages/OES-RC-0005-R4/privacy_boundary_check.py
python specification/packages/OES-RC-0005-R4/scope_check.py
python specification/packages/OES-RC-0005-R4/collision_check.py /path/to/OES007_baseline_repo_root
```

## Expected Result

All commands must return PASS.

## Important

`collision_check.py` requires a baseline repository root. It must not silently pass without comparing against the commit-target baseline.


## R4 Procedural Fixes

* Validators normalize paths using POSIX separators for Windows/POSIX reproducibility.
* Backend-applied ZIP is regenerated without nested handoff/audit ZIP contamination.
* Central privacy, deny-by-default and learning-signal policies are unchanged.
