# OEP-004.2 — Distiller Batch + Idempotency Check

## Objetivo

Adicionar processamento em lote ao Conversation Distiller com chave de idempotência determinística.

## Escopo

Backend-only.

Não toca:
- `/api/chat`
- `/api/chat/stream`
- realtime
- voice
- frontend
- banco de dados

## Arquivos

- `evolution/conversation/idempotency.py`
- `evolution/conversation/batch.py`
- `evolution/conversation/__init__.py`
- `tests/oep004_2_batch_idempotency_smoke.py`

## Resultado esperado

```txt
OEP004_2_BATCH_IDEMPOTENCY_PASS
```

## Rollback

```bash
git restore evolution/conversation/__init__.py
rm -f evolution/conversation/batch.py
rm -f evolution/conversation/idempotency.py
rm -f tests/oep004_2_batch_idempotency_smoke.py
rm -f docs/OEP004_2_BATCH_IDEMPOTENCY.md
```
