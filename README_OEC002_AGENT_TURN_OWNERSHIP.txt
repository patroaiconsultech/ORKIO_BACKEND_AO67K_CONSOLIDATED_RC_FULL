ORKIO — OEC-002 AGENT TURN OWNERSHIP

OBJETIVO
Corrigir a autoria do turno quando Orion é selecionado, sem remover o pipeline
governado e sem alterar permissões de escrita, merge, deploy ou banco.

ARQUIVOS
- main.py (completo)
- runtime/agent_turn_context.py (novo)
- tests/test_oec002_agent_turn_ownership.py (novo)
- docs/orion/OEC002_AGENT_TURN_OWNERSHIP.md
- OEC002_AGENT_TURN_OWNERSHIP.diff

COMPORTAMENTO ESPERADO
Quando requested_agent=orion:
- orchestrator_agent=orkio
- turn_owner=orion
- display_agent=orion
- technical_lead=orion
- ownership_locked=true
- persistência da resposta com agent_id=orion e agent_name=Orion

Quando nenhum agente interno é selecionado:
- Orkio continua como proprietário e agente exibido.

GOVERNANÇA PRESERVADA
- proposal_only
- approval obrigatório
- write bloqueado conforme flags
- merge bloqueado conforme flags
- deploy bloqueado conforme flags
- schema direto bloqueado

VALIDAÇÃO
python -m pytest -q tests/test_oec002_agent_turn_ownership.py
Esperado: 3 passed

LOG ESPERADO
AO01_AGENT_TURN_OWNERSHIP
requested_agent=orion
orchestrator_agent=orkio
turn_owner=orion
display_agent=orion
technical_lead=orion
route_family=governed_evolution_pipeline
ownership_locked=True

ROLLBACK
1. Restaurar main.py para a revisão anterior.
2. Remover runtime/agent_turn_context.py.
3. Remover tests/test_oec002_agent_turn_ownership.py.
Nenhuma migration ou alteração de dados.
