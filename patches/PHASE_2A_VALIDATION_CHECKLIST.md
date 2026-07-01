# Phase 2A Validation Checklist

## Pre-commit

- [ ] Remove `__pycache__`
- [ ] Remove `*.pyc`
- [ ] Confirm no secrets
- [ ] Confirm no route changes
- [ ] Confirm no frontend changes

## Commands

```bash
python -m compileall app tests
python -m pytest -q
```

## Expected

- compileall OK
- pytest OK
- no production behavior changed

## GO / NO-GO

GO:
- package added as isolated modules
- tests passing
- no changes to productive routes

NO-GO:
- `/api/chat` changed
- `/api/chat/stream` changed
- auth changed
- DB migration added without approval
- automatic execution enabled
