# EPIC-002E — SERVICES IMPORT HYGIENE TARGET LOCKED

## Objetivo

Resolver exclusivamente o próximo bloqueio integrado confirmado:

`services.governance_service → app.services.capability_service → ModuleNotFoundError`

## Estado

SHADOW / TARGET-ONLY.

## Alvo

- `services/governance_service.py`

## Não escopo

- Não corrigir todos os imports `app.*` do repositório.
- Não alterar runtime behavior.
- Não tocar `main.py`.
- Não tocar SSE.
- Não tocar persistência.
- Não criar shim.
- Não usar fallback.

## Critérios de aceite

1. Aplicador `--check` executa.
2. Aplicador `--write` altera somente o alvo.
3. Segunda aplicação é idempotente.
4. Auditoria target-only passa.
5. Teste executável passa.
6. Manifesto SHA256 confere.
7. ZIP sem cache Python.

## Risco residual

A cadeia integrada pode revelar outro import legado após este elo. Esse próximo bloqueio deve ser tratado em EPIC separado.
