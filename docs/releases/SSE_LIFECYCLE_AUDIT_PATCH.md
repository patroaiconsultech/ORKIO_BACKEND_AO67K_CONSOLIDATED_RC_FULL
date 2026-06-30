# SSE Lifecycle Audit Patch

## Objective

Add minimal and premium audit markers to the `/api/chat/stream` lifecycle without changing runtime behavior.

## Scope

- `main.py` instrumentation only.
- No API contract change.
- No database change.
- No frontend change.
- No timeout increase.
- No runtime logic change.

## Markers

- `SSE_STATUS_YIELD_ATTEMPT`
- `SSE_STREAM_EXIT_REACHED`
- `CLIENT_CANCELLED_BEFORE_FIRST_EVENT`

## Validation

```bash
python tools/apply_sse_lifecycle_audit_patch.py
PYTHONPATH=. python -m py_compile main.py tools/apply_sse_lifecycle_audit_patch.py tests/sse_lifecycle_audit_smoke.py tests/regression/sse_lifecycle_audit_suite.py
PYTHONPATH=. pytest tests/sse_lifecycle_audit_smoke.py
PYTHONPATH=. python tests/regression/sse_lifecycle_audit_suite.py
git diff --stat main.py
```

Expected diff for `main.py`: small insertion-only audit patch.

## Rollback

```bash
git checkout -- main.py
rm -f tools/apply_sse_lifecycle_audit_patch.py tests/sse_lifecycle_audit_smoke.py tests/regression/sse_lifecycle_audit_suite.py docs/releases/SSE_LIFECYCLE_AUDIT_PATCH.md
```
