# READONLY_AUDIT Request — OES-008 / OES-RC-0005-R4

## Context

OES-RC-0005-R3 received YELLOW / NO-GO due to two procedural issues:

1. the delivered validator scripts were not reproducible on Windows because path comparisons used `str(Path(...))` against `specification/`;
2. the loose backend-applied ZIP in Downloads was contaminated with an embedded handoff ZIP, even though the backend embedded inside the handoff was correct.

R4 is a patch-minimum release. It does not change the central privacy, deny-by-default or learning-signal policies.

## Audit Scope

Please verify:

1. `manifest_check.py`, `scope_check.py`, and `collision_check.py` normalize relative paths with `.as_posix()` or equivalent logic.
2. The validators pass in Windows/POSIX-compatible path semantics.
3. `collision_check.py` still authenticates the baseline by hashing:
   `specification/OES-007_CONTRACT_EVENT_PROJECTION.md`
   and requiring:
   `C67F471AAA59D0EAF57F791ED43679D0714D990903CC927A4FAE18DCD8A88B26`
4. The checker fails if the OES-RC-0004-R1 package is absent from the baseline.
5. The checker fails if OES-008/R4 paths already exist in the baseline.
6. The R4 added-files diff is a valid unified diff and remains reproducible with `git apply --check`.
7. The loose backend-applied ZIP is not contaminated and does not include handoff/audit ZIPs.
8. No raw private content is included.
9. The source candidate remains `metadata_only_without_content_access`.
10. The Learning Signals Policy still permits learning only from sanitized operational signals.
11. No runtime, API, database or infrastructure files were changed.
12. The repo-ready package and applied backend are equivalent byte-by-byte for the R4 files.
13. The manifest and SHA256SUMS are valid.

## Restrictions

* Do not alter files.
* Do not commit.
* Do not push.
* Do not open PRs.
* Do not deploy.

## Expected Result

GREEN / YELLOW / RED with GO / NO-GO.
