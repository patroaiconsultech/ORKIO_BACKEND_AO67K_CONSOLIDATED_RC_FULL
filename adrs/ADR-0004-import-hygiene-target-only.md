# ADR-0004 — Import Hygiene Target-Only

## Status

Accepted for Shadow.

## Contexto

A validação integrada do EPIC-002B é bloqueada por imports legados em `runtime/intent_engine.py`.

## Decisão

Corrigir somente o alvo que bloqueia a importação inicial, usando aplicador Python
idempotente em vez de patch textual.

## Consequências

- Evita patch corrompido
- Evita limpeza global prematura
- Mantém escopo auditável
- Expõe o próximo bloqueio real (`app.core`) para EPIC separado
