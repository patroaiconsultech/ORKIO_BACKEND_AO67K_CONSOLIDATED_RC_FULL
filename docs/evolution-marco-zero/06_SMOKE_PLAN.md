# Smoke MZ-001-R1

## Antes do deploy

```bash
python -m py_compile   main.py   tests/test_evolution_marco_zero_static.py   tests/test_evolution_marco_zero_preview.py

python -m pytest -q   tests/test_evolution_marco_zero_static.py   tests/test_evolution_marco_zero_preview.py   tests/test_evolution_signal_service.py   tests/test_evolution_signal_routes.py   tests/test_sec001_access_grants.py   tests/test_sec001_mutation_fail_closed.py
```

Resultado reproduzido:

```text
26 passed
```

## Deploy inicial

```text
EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED=false
```

Confirmar boot e canary.

## Ativar preview

```text
EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED=true
```

## HTTP

```text
sem token → 401
não-admin → 403
tenant divergente → 403
admin + dry_run=true → 200
admin + dry_run=false → 403
```

## Banco

Antes e depois de dez previews:

```sql
SELECT COUNT(*) FROM admin_evolution_proposals;
SELECT COUNT(*) FROM admin_evolution_proposals WHERE status = 'archived';
```

Esperado:

```text
total_delta=0
archived_delta=0
```
