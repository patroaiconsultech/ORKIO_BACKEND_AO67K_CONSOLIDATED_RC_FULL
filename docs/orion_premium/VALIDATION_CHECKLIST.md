# Validation Checklist

- [ ] Aplicar em branch dedicada.
- [ ] Iniciar em shadow mode.
- [ ] Upload com extração válida retorna `document_evidence_based`.
- [ ] Arquivo sem extração retorna `document_hypothesis_only`.
- [ ] Nenhum arquivo retorna `no_document_attached`.
- [ ] `runtime_hints.orion_premium.document_grounding` está presente.
- [ ] Rota `/api/chat` permanece funcional.
- [ ] Rota `/api/chat/stream` mantém eventos e liberação do input.
- [ ] Mensagem assistant continua persistida.
- [ ] Testes focados passam.
- [ ] Testes de regressão existentes passam.
- [ ] Fail-closed ativado somente após staging.
