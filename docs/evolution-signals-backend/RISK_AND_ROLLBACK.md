# Riscos e rollback

## Risco eliminado

Não substituir o `main.py` da produção `(41)` pelo `main.py` construído sobre `(40)`.

Este pacote já contém o `main.py` da produção `(41)` com patch cirúrgico.

## Riscos restantes

1. Migration aplicada sem backup.
2. Deploy antes da migration.
3. Flags de escrita ativadas prematuramente.
4. Divergência entre `(41)`, `origin/main` e commit Railway.
5. Falta de teste PostgreSQL multi-réplica antes de habilitar POSTs.

## Rollback operacional

```text
EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED=false
EVOLUTION_AGENT_EVAL_WRITE_ENABLED=false
```

## Rollback de código

Reverter o commit do PR.

## Rollback da migration

Somente após confirmar que não há dados a preservar:

```bash
python -m alembic downgrade 0036_patch_file_requests_reconcile
```

O downgrade remove somente:

```text
platform_evolution_metric_snapshots
agent_capability_evaluations
```
