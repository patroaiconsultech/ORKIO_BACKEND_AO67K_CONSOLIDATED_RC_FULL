# ORKIO CORE RC2-R2 — Runtime Foundation

Status: `shadow_candidate`.

Baseline SHA locked:

```text
94ba9246bcd3d2a5c40d42657ae7ca17c80a2826
```

This package consolidates the approved EPIC-002A..002F runtime foundation work into a single auditable release candidate.

## Included

- Runtime Persistence Foundation shadow payload
- Canonical deterministic `assistant_message_id`
- Target-only import hygiene for the chain required by EPIC-002B integrated import
- Baseline SHA guard
- Consolidated validator
- Engineering binder summary
- ADR index
- Rollback plan
- Validation checklist

## Not included

- No production promotion
- No guarded/enforcement activation
- No `main.py` changes
- No SSE changes
- No DB migrations
- No shim
- No fallback `{}`
- No new authority
- No new router
- No new guard

## Official commands

From repository root, after extracting this package:

```bash
python tools/apply_shadow_candidate.py --repo . --check
python tools/apply_shadow_candidate.py --repo . --write
python tools/apply_shadow_candidate.py --repo . --write
python tools/validate_shadow_candidate.py --repo .
pytest -p no:cacheprovider tests/runtime/test_runtime_persistence_shadow.py
pytest -p no:cacheprovider <path-to-package>/tests/test_rc2_shadow_candidate_sha_guard.py
```

Expected status: GO for branch/shadow only. NO-GO for guarded/enforcement/production.
