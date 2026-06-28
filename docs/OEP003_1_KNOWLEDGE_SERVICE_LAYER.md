# OEP-003.1 — Knowledge Service Layer

## Objetivo
Criar uma camada pública e reutilizável para o Knowledge Vault, preparando o OEP-004 Conversation Distiller.

## Arquitetura

```text
evolution.knowledge
        ↓
KnowledgeService
        ↓
InMemoryKnowledgeRepository
        ↓
KnowledgeVault
```

## Critério de aceite
O smoke test deve retornar:

```text
OEP003_1_KNOWLEDGE_SERVICE_LAYER_PASS
```

## Risco
Baixo. Patch isolado em `evolution/` e `tests/`.

## Rollback
Remover os arquivos adicionados neste patch.
