# OEP-004.3 — Conversation Intake Governance

## Objetivo

Adicionar uma fronteira governada antes do Conversation Distiller.

Este patch cria:

- contrato de intake com tenant, user, thread e consentimento;
- hash de conteúdo;
- chave de idempotência determinística;
- scan/redação simples de PII;
- wrapper governado para chamar o distiller sem tocar chat, realtime, voice ou banco.

## Arquivos

- `evolution/conversation/intake.py`
- `evolution/conversation/privacy.py`
- `evolution/conversation/governed_distiller.py`
- `tests/oep004_3_conversation_intake_governance_smoke.py`

## Escopo preservado

Não altera:

- `/api/chat`
- `/api/chat/stream`
- frontend
- realtime
- voice
- banco
- migrations

## Validação

```bash
PYTHONPATH=. python -m py_compile evolution/*.py evolution/conversation/*.py tests/oep004_3_conversation_intake_governance_smoke.py
PYTHONPATH=. python tests/oep004_3_conversation_intake_governance_smoke.py
```

Saída esperada:

```txt
OEP004_3_CONVERSATION_INTAKE_GOVERNANCE_PASS
```

## Rollback

Remover:

- `evolution/conversation/intake.py`
- `evolution/conversation/privacy.py`
- `evolution/conversation/governed_distiller.py`
- `tests/oep004_3_conversation_intake_governance_smoke.py`
- `docs/OEP004_3_CONVERSATION_INTAKE_GOVERNANCE.md`
