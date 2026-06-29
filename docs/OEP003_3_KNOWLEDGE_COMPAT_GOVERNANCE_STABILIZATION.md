# OEP-003.3 — Knowledge Compatibility & Governance Stabilization

## Objetivo
Estabilizar a fundação OEP-003.x antes do OEP-004 Conversation Distiller.

## Correções
- Restaura facade `KnowledgeEngine` para compatibilidade com `EvolutionEngine`.
- Restaura `KNOWLEDGE_MODULE_MANIFEST`.
- Usa uma única instância de `KnowledgeManifest` via `KnowledgeRepository`.
- Remove duplicidade de responsabilidade em `KnowledgeService`.
- Mantém validação explícita de governança com exceções, não `assert`.
- Remove auto-save em `KnowledgeVault.add_document()`.
- `KnowledgeVault.save()` marca o snapshot de disco com `write_executed=True`.
- Adiciona smoke de compatibilidade do EvolutionEngine.

## Fora de escopo
- Chat
- Realtime
- Voice
- Frontend
- Banco
- OEP-004
