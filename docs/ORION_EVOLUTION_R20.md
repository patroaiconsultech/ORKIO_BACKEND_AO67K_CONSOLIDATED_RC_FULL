ORION EVOLUTION R20 — PLANO MÍNIMO AO PREMIUM

OBJETIVO
Transformar a capacidade atual de proposal_only em um pipeline premium governado,
sem habilitar escrita automática em produção.

ESTADO INCORPORADO
1. Contratos estruturados:
   - EvolutionPlan
   - RiskAssessment
   - RollbackPlan
   - SimulationReport

2. Pipeline:
   proposal_only
   -> simulation
   -> human approval
   -> isolated branch gate
   -> dry-run/apply gate

3. Guardrails:
   - produção sempre bloqueada
   - risco alto bloqueado para board manual
   - branch isolada obrigatória
   - diff, testes e rollback obrigatórios
   - write_executed permanece false
   - branch_apply exige ORION_BRANCH_EXECUTION_ENABLED=true

4. Escopo R20:
   - cria e valida planos
   - calcula risco
   - simula contratos
   - registra aprovação humana
   - decide se um executor externo poderia atuar em branch
   - NÃO escreve arquivos
   - NÃO cria branch
   - NÃO faz commit/push
   - NÃO faz deploy

ARQUIVOS NOVOS
- evolution/premium_contracts.py
- evolution/premium_risk.py
- evolution/premium_simulation.py
- evolution/premium_guard.py
- evolution/premium_pipeline.py
- tests/test_orion_premium_evolution_r20.py

ARQUIVO ALTERADO
- evolution/__init__.py

PRÓXIMA FASE R21
Implementar executor de branch isolada com:
- workspace temporário
- git diff real
- allowlist de caminhos
- testes em subprocesso com timeout
- commit local sem push automático
- artefato de evidência
- aprovação humana separada para push/PR

ROLLBACK
git revert <sha-do-r20>

VEREDITO
R20 habilita o núcleo premium governado, mas mantém autonomia de escrita em L1:
proposta + simulação + aprovação + gate. Produção permanece NO-GO automático.
