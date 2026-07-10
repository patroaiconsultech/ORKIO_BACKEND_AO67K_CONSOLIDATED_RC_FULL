ORKIO — AO-01 ROUTE DECISION DIAGNOSTIC V1

OBJETIVO
Identificar, em produção, qual arquivo, função e versão realmente decidiram a
route_family de cada requisição em /api/chat/stream.

ESCOPO
Instrumentação somente. Este patch NÃO altera:
- classificação;
- handled=True/False;
- templates;
- provider LLM;
- SSE;
- persistência;
- banco;
- frontend.

ARQUIVOS PARA O REPOSITÓRIO
1. main.py
2. runtime/orkio_stream_precedence.py
3. tests/test_ao01_route_decision_diagnostic.py

LOG NOVO
Cada requisição ao stream produzirá uma linha iniciada por:

AO01_ROUTE_DECISION

Campos principais:
- trace_id
- handled
- category
- route_family
- guard_route_family
- guard_version
- guard_module
- guard_function
- guard_source_file
- guard_source_sha256
- stream_adapter_file
- stream_integration_version
- message_chars
- message_lines

VALIDAÇÃO LOCAL
pytest -q tests/test_ao01_route_decision_diagnostic.py

RESULTADO VALIDADO
2 passed

TESTE PÓS-DEPLOY
Executar apenas o primeiro prompt complexo e localizar a linha:
AO01_ROUTE_DECISION trace_id=...

INTERPRETAÇÃO
1. handled=True + executive_strategy_answer:
   o guard carregado realmente decidiu pelo template.
2. handled=False + guard_route_family=context_aware_llm_answer:
   o bypass funcionou; outra camada posterior está gerando o template.
3. guard_version diferente da revisão esperada:
   produção carregou arquivo/versão divergente.
4. guard_source_file diferente de /app/runtime/orkio_executive_guard.py:
   existe colisão ou import de outro módulo.
5. guard_source_sha256 inesperado:
   o arquivo em memória não corresponde ao arquivo esperado no GitHub.

ROLLBACK
Restaurar:
- main.py
- runtime/orkio_stream_precedence.py

Remover:
- tests/test_ao01_route_decision_diagnostic.py

Nenhuma migration ou alteração de dados precisa ser revertida.
