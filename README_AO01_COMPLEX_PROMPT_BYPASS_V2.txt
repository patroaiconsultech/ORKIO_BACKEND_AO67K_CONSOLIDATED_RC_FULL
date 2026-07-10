ORKIO — AO-01 COMPLEX PROMPT BYPASS V2

OBJETIVO
Impedir que templates determinísticos encerrem antecipadamente pedidos complexos,
multiobjetivo, com cenários, cálculos compostos ou várias entregas.

ARQUIVOS PARA O REPOSITÓRIO
1. runtime/orkio_executive_guard.py
2. tests/test_ao01_complex_prompt_bypass_v2.py

ALTERAÇÃO CIRÚRGICA
- Adiciona marcadores explícitos de complexidade.
- Executa o bypass antes de dashboard, crise, estratégia e matemática.
- Mantém a heurística anterior como segunda proteção.
- Preserva templates para perguntas simples e estreitas.
- Atualiza ORKIO_EXECUTIVE_GUARD_VERSION para AO01_COMPLEX_PROMPT_BYPASS_V2.

TESTE
pytest -q tests/test_ao01_complex_prompt_bypass_v2.py

RESULTADO ESPERADO
4 passed

LOG ESPERADO NOS TRÊS PROMPTS COMPLEXOS
Não deve aparecer:
route_family=executive_strategy_answer
route_family=executive_quantitative_answer
route_family=executive_dashboard_answer

O guard deve retornar handled=False e o fluxo deve continuar para o runtime LLM.

ROLLBACK
Restaurar somente runtime/orkio_executive_guard.py para a revisão anterior e
remover tests/test_ao01_complex_prompt_bypass_v2.py.

RISCO
Baixo. Não altera frontend, SSE, banco, migrations, autenticação ou provider.
