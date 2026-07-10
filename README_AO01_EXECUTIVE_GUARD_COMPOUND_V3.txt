ORKIO — AO-01 EXECUTIVE GUARD COMPOUND V3

OBJETIVO
Impedir que prompts compostos, multiobjetivo ou com várias entregas sejam
capturados pelo template executivo quantitativo.

CAUSA COMPROVADA
O log de produção classificou o prompt complexo como:
category=quantitative_business_math
route_family=executive_quantitative_answer

ALTERAÇÃO
1. Cria _is_compound_executive_request().
2. Executa uma trava fail-open no início de eos06_build_router_precedence_payload().
3. Faz _looks_like_financial_math_request() rejeitar prompts compostos.
4. Mantém cálculo simples e estratégia simples nos templates existentes.
5. Publica a assinatura:
   ORKIO_EXECUTIVE_GUARD_VERSION=AO01_EXECUTIVE_GUARD_COMPOUND_V3

ARQUIVOS
- runtime/orkio_executive_guard.py
- tests/test_ao01_executive_guard_compound_v3.py
- AO01_EXECUTIVE_GUARD_COMPOUND_V3.diff

VALIDAÇÃO
python -m pytest -q tests/test_ao01_executive_guard_compound_v3.py

ESPERADO
3 passed

PROVA PÓS-DEPLOY
Para o prompt complexo, o log deve mostrar:
category=full_llm_runtime_required
route_family=context_aware_llm_answer
force_full_llm_runtime=True
guard_version=AO01_EXECUTIVE_GUARD_COMPOUND_V3

NÃO DEVE MOSTRAR
category=quantitative_business_math
route_family=executive_quantitative_answer

ROLLBACK
Restaurar somente runtime/orkio_executive_guard.py para a revisão anterior.
Remover o teste V3. Não há alteração de banco, migration ou frontend.
