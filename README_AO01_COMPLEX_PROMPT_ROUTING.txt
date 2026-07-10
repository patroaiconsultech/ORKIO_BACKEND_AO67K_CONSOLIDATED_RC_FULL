ORKIO AO-01 — PATCH DE ROTEAMENTO PARA PROMPTS COMPLEXOS

OBJETIVO
Impedir que templates determinísticos de estratégia, dashboard ou matemática
encerrem antecipadamente prompts complexos, multiobjetivo ou com análise de cenários.

ARQUIVOS
1. runtime/orkio_executive_guard.py
2. tests/test_ao01_complex_prompt_routing.py

COMPORTAMENTO
- Pedidos curtos e estreitos continuam usando os templates existentes.
- Pedidos com várias entregas, cenários, sensibilidade ou cálculos compostos
  retornam handled=False no guard.
- O fluxo normal do backend continua e envia o pedido integral ao runtime LLM.
- Nenhuma alteração em frontend, SSE, banco, migrations ou provider.

TESTE
pytest -q tests/test_ao01_complex_prompt_routing.py

LOG ESPERADO APÓS DEPLOY
Para prompts complexos, NÃO deve aparecer:
  route_family=executive_strategy_answer
  route_family=executive_quantitative_answer

O fluxo deve seguir para o runtime normal do modelo.

ROLLBACK
Restaurar apenas runtime/orkio_executive_guard.py para a versão anterior e
remover tests/test_ao01_complex_prompt_routing.py.
