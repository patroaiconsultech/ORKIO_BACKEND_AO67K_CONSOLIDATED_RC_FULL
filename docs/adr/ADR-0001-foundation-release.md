# ADR-0001 — ORKIO OS 1.0 Foundation Release

## Status

Accepted for proposal_only implementation.

## Contexto

O histórico recente mostrou acoplamento entre runtime, decisão cognitiva, persistência e conhecimento.

## Decisão

Criar fundação modular com Executive Kernel, Runtime Foundation, Knowledge Fabric e Governance.

## Consequências

- `main.py` deve permanecer como entrypoint.
- Decisão cognitiva deve migrar para `runtime/orkio_kernel`.
- Persistência deve ser idempotente.
- Knowledge Fabric não deve consultar Drive diretamente em runtime.
