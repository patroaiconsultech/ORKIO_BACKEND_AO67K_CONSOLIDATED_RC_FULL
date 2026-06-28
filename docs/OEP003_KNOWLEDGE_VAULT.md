# OEP-003 — Knowledge Vault

## Objetivo

Criar a fundação backend-only para armazenamento estruturado de conhecimento,
indexação e busca, preparando o ORKIO para o Conversation Distiller (OEP-004).

## Escopo

Inclui:

- `evolution/knowledge_vault.py`
- `evolution/knowledge.py`
- `tests/oep003_knowledge_vault_smoke.py`

Não inclui:

- integração com `/api/chat`
- integração com `/api/chat/stream`
- realtime
- voice
- Team
- frontend
- rotas públicas

## Contrato de segurança

Todos os documentos e snapshots mantêm:

```txt
proposal_only=True
write_executed=False
human_approval_required=True
```

## Validação

No backend:

```bash
PYTHONPATH=. python -m py_compile evolution/*.py tests/oep003_knowledge_vault_smoke.py
PYTHONPATH=. python tests/oep003_knowledge_vault_smoke.py
```

Resultado esperado:

```txt
OEP003_KNOWLEDGE_VAULT_SMOKE_PASS
```

## Rollback

Remover:

```txt
evolution/knowledge_vault.py
tests/oep003_knowledge_vault_smoke.py
docs/OEP003_KNOWLEDGE_VAULT.md
```

Se `evolution/knowledge.py` já existir no repo, restaurar a versão anterior pelo Git.
