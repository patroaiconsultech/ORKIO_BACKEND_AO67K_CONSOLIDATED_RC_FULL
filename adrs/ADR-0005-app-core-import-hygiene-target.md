# ADR-0005 — App Core Import Hygiene Target

## Status

Accepted for SHADOW ONLY.

## Contexto

Após EPIC-002C-R2, a cadeia integrada avançou até:

```text
services.governance_service
→ app.core.orkio_constitution
→ ModuleNotFoundError
```

## Decisão

Normalizar somente o alvo `services/governance_service.py`, trocando `app.core.*` por `core.*`.

## Consequências

- reduz uma camada de dívida de namespace;
- mantém escopo mínimo;
- evita shims;
- não resolve toda a árvore de imports;
- qualquer próximo bloqueio deve virar novo EPIC target-only.
