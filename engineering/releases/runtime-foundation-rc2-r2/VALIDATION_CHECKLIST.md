# Validation Checklist — RC2 Runtime Foundation

- [ ] Confirm `git rev-parse HEAD == 94ba9246bcd3d2a5c40d42657ae7ca17c80a2826`.
- [ ] `python tools/apply_shadow_candidate.py --check`
- [ ] `python tools/apply_shadow_candidate.py --write`
- [ ] Repeat write: idempotent PASS or PASS_NOOP.
- [ ] `python tools/validate_shadow_candidate.py`
- [ ] `pytest tests/runtime/test_runtime_persistence_shadow.py`
- [ ] Import Runtime Foundation.
- [ ] Smoke Runtime Foundation.
- [ ] Confirm `main.py` unchanged.
- [ ] Confirm no `app/config/runtime.py`.
- [ ] Confirm no DB migration.
- [ ] Confirm no SSE edits.
- [ ] Confirm manifest integrity.

## RC2-R2 Additional Checks

- [ ] `--skip-sha-check` is not accepted by the applier.
- [ ] Pre-existing `app/config/runtime.py` is rejected before any write.
- [ ] SHA guard tests pass with monkeypatch-based subprocess validation.


## RC2-R2 Artifact Hygiene Checks

- [ ] Confirm `.pytest_cache/` is absent from ZIP and extracted tree.
- [ ] Confirm no `__pycache__`, `.pyc`, or `.pyo` files.
- [ ] Run package tests with `pytest -p no:cacheprovider`.
- [ ] Confirm `MANIFEST_SHA256.txt` does not include cache files.
