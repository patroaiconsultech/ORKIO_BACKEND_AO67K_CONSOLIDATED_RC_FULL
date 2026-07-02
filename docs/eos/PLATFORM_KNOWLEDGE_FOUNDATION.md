# Platform Knowledge Foundation — ORKIO

## Objetivo

Criar uma fonte oficial, versionada e governada sobre o que a plataforma Orkio é, oferece hoje, mantém em beta e planeja para roadmap.

## Problema resolvido

Evitar que o Orkio responda por inferência, misturando:

- produção;
- beta;
- roadmap;
- proposta conceitual;
- histórico de documentos.

## Entregáveis

- `knowledge/platform/platform_manifest.yaml`
- `knowledge/platform/current_capabilities.yaml`
- `knowledge/platform/roadmap_registry.yaml`
- `knowledge/platform/response_policy.yaml`
- `knowledge/platform/governance_rules.yaml`
- `runtime/platform_knowledge_contract.py`

## Próxima integração

Conectar `platform_answer_guard()` antes de respostas públicas sobre a plataforma.
