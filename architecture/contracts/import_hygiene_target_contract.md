# Contrato — Import Hygiene Target

## Autoridade

Este contrato não cria nova autoridade de runtime.
Ele apenas define regra de higiene de imports para um alvo específico.

## Escopo

```text
services/governance_service.py
```

## Regra

Imports legados `app.core.*` no alvo devem ser normalizados para `core.*`, quando `core/orkio_constitution.py` existir no baseline.

## Proibições

- criar pacote `app.core`;
- criar shim;
- fallback silencioso;
- alterar lógica de negócio;
- alterar `main.py`;
- alterar SSE;
- alterar persistência;
- impor limpeza global neste EPIC.

## Fail-closed

Se `core/orkio_constitution.py` não existir, o aplicador deve falhar e exigir auditoria manual.
