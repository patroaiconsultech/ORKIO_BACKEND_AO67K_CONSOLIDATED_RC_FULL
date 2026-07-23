ORKIO / ORION — PACOTE CONSOLIDADO R21–R25
TIPO: PATCH-ONLY (somente arquivos novos e alterados)

OBJETIVO
Incorporar o subsistema Orion modular com:
- contratos auditáveis;
- governança;
- workspace isolado;
- allowlist de caminhos;
- política de comandos;
- scanner de repositório;
- grafo da plataforma;
- diagnóstico;
- planejamento;
- geração e validação de diff;
- laboratório de validação;
- memória evolutiva;
- máquina de estados;
- event bus;
- adaptador de compatibilidade R20.

GARANTIAS
- Produção bloqueada.
- Git push bloqueado.
- Deploy bloqueado.
- Repositório principal sem permissão de escrita.
- Aprovação humana obrigatória.
- Paths sensíveis bloqueados.
- Shell arbitrário bloqueado.
- Kernel somente orquestra.
- Memória não altera política ou permissões.

NOVOS
orion/__init__.py
orion/contracts/__init__.py
orion/contracts/models.py
orion/contracts/protocols.py
orion/governance/__init__.py
orion/governance/permission_matrix.py
orion/governance/risk_engine.py
orion/governance/execution_guard.py
orion/execution/__init__.py
orion/execution/path_allowlist.py
orion/execution/command_policy.py
orion/execution/workspace_manager.py
orion/execution/patch_executor.py
orion/perception/__init__.py
orion/perception/repository_scanner.py
orion/knowledge/__init__.py
orion/knowledge/platform_graph.py
orion/reasoning/__init__.py
orion/reasoning/diagnosis_engine.py
orion/planning/__init__.py
orion/planning/proposal_builder.py
orion/engineering/__init__.py
orion/engineering/diff_generator.py
orion/engineering/patch_validator.py
orion/validation/__init__.py
orion/validation/validation_lab.py
orion/learning/__init__.py
orion/learning/evolution_memory.py
orion/strategy/__init__.py
orion/strategy/priority_engine.py
orion/kernel/__init__.py
orion/kernel/state_machine.py
orion/kernel/event_bus.py
orion/kernel/cognitive_kernel.py
orion/adapters/__init__.py
orion/adapters/evolution_r20_adapter.py
tests/test_orion_r21_r25_governance.py
tests/test_orion_r21_r25_kernel.py
tests/test_orion_r21_r25_engineering.py
tests/test_orion_r21_r25_learning_adapter.py
docs/ORION_R21_R25.md

ALTERADO
evolution/__init__.py

APLICAÇÃO
Extrair o ZIP na raiz do repositório R20, preservando a estrutura.
O único arquivo existente substituído será evolution/__init__.py.

VALIDAÇÃO
python -m pytest -q   tests/test_orion_r21_r25_governance.py   tests/test_orion_r21_r25_kernel.py   tests/test_orion_r21_r25_engineering.py   tests/test_orion_r21_r25_learning_adapter.py   tests/test_orion_premium_evolution_r20.py

ROLLBACK
1. Remover o diretório orion/.
2. Remover os quatro testes R21–R25.
3. Restaurar evolution/__init__.py do commit anterior.
4. Remover docs/ORION_R21_R25.md.

LIMITAÇÃO INTENCIONAL
O pacote não conecta Orion ao main.py, API pública, scheduler ou deploy.
Essa integração deve ocorrer somente após validação do pacote em branch.
