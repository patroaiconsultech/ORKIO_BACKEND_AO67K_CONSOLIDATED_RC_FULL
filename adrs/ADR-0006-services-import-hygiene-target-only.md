# ADR-0006 — Services Import Hygiene Target-Only

## Status

Accepted for SHADOW target-only.

## Contexto

Após EPIC-002D-R1, o import integrado avançou e parou em:

`services.governance_service → app.services.capability_service`

## Decisão

Corrigir somente esse elo, usando aplicador idempotente e auditoria target-only.

## Consequências

A cadeia de imports avança sem mascarar dívida técnica restante. Novos bloqueios devem virar EPICs separados.
