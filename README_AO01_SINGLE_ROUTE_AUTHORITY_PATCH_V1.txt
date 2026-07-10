ORKIO — AO-01 SINGLE ROUTE AUTHORITY PATCH V1
Data: 2026-07-10

OBJETIVO
Tornar vinculante a decisão de encaminhar prompts complexos ao runtime completo
do LLM, impedindo recaptura por templates determinísticos posteriores.

ARQUIVOS ALTERADOS
1. main.py
2. runtime/orkio_stream_precedence.py
3. runtime/orkio_executive_guard.py

ARQUIVO DE TESTE
4. tests/test_ao01_single_route_authority.py

CAUSA RAIZ CORRIGIDA
O mesmo turno era reclassificado por múltiplos corredores:
- stream-entry executive guard;
- Decision Mesh;
- jornada pública;
- HF4K/HF1 executive precedence;
- governed_evolution_pipeline.

Quando o primeiro gate retornava handled=False, essa decisão não era vinculante.
Camadas posteriores podiam assumir o turno e retornar templates estáticos.

COMPORTAMENTO NOVO
Para prompt complexo:
- category=full_llm_runtime_required
- route_family=context_aware_llm_answer
- force_full_llm_runtime=true
- block_executive_templates=true
- block_public_deterministic_fastpaths=true
- block_governed_evolution_fastpath=true

Os seguintes corredores ficam bloqueados somente nesse caso:
- AO67F Decision Mesh gateway;
- AO66B public journey;
- HF4K/HF1 executive guard;
- governed_evolution_pipeline.

Prompts simples continuam usando templates determinísticos.

LOG ESPERADO
AO01_SINGLE_ROUTE_DECISION
Campos:
- trace_id
- handled
- category
- route_family
- force_full_llm_runtime
- guard_version
- guard_source_file
- guard_source_sha256

VALIDAÇÃO
python -m pytest -q tests/test_ao01_single_route_authority.py

RESULTADO OBTIDO
2 passed

SMOKE TEST PÓS-DEPLOY
1. Executar um prompt complexo.
2. Confirmar:
   AO01_SINGLE_ROUTE_DECISION ... force_full_llm_runtime=True
3. Confirmar ausência de:
   MANUS_UX_R3_2_STREAM_ENTRY_TURN_OWNERSHIP
   EOS06_AO85_HF1_FASTPATH_PRECEDENCE
   EOS06_AO85_HF1_ROUTER_PRECEDENCE
   AO67F_ORKIO_DECISION_MESH_GATEWAY_FASTPATH
   AO66B_AMCHAM_PUBLIC_JOURNEY_FASTPATH
   stream_ao20j_governed_evolution_pipeline
4. Confirmar chamada ao provider e resposta completa.
5. Confirmar status → chunk → agent_done → done.
6. Confirmar persistência após reload e input liberado.

RISCO
Baixo a médio:
- prompts complexos passarão a consumir tokens reais;
- latência pode aumentar;
- prompts simples permanecem no fast-path.

ROLLBACK
Restaurar os três arquivos alterados:
- main.py
- runtime/orkio_stream_precedence.py
- runtime/orkio_executive_guard.py

Remover o teste.
Nenhuma migration ou alteração de dados precisa ser revertida.
