# Orion Premium — Phase 1 Delta

Este pacote contém somente arquivos novos ou alterados em relação ao backend enviado.

## Aplicação

Copie os arquivos preservando os caminhos relativos. O `main.py` deste pacote substitui o `main.py` atual.

## Configuração inicial recomendada

```env
ORION_DOCUMENT_EVIDENCE_GUARD_ENABLED=true
ORION_PREMIUM_SHADOW_MODE=true
ORION_REQUIRE_EXECUTION_RECEIPT=true
ORION_REQUIRE_HUMAN_APPROVAL=true
ORION_MIN_LEARNING_CONFIDENCE=0.70
```

Em shadow mode, o comportamento atual é preservado e a decisão aparece em:

`runtime_hints.orion_premium.document_grounding`

Após validação em staging:

```env
ORION_PREMIUM_SHADOW_MODE=false
```

## Escopo

- grounding documental determinístico;
- fail-closed opcional;
- recibos de execução;
- propostas de aprendizado governado;
- testes focados.

Não altera banco, schema, upload, RAG ou contrato SSE.
