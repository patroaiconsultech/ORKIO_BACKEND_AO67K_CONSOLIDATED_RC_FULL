ORKIO — EGA-005 UNIFIED MUTATION GOVERNANCE

OBJETIVO
Unificar o patch mínimo de segurança e a fundação premium de governança em um
único pacote progressivo e reversível.

O QUE O PATCH FAZ

P0 — Segurança imediata
1. AUTO_SCHEMA_HOTFIX_DIRECT passa a usar default False.
2. O health endpoint também informa False por default.
3. Nenhum deploy é autorizado pelo novo gate.
4. Alteração direta de schema permanece desligada.

P1 — Mutation Authority Gate
Cria:
evolution_os/governance/mutation_authority.py

O gate valida:
- ação conhecida;
- feature flag específica por ação;
- proposal_id;
- approval_id;
- status approved;
- approved_by persistido;
- approved_at persistido;
- TTL de aprovação;
- ator executor;
- dry_run_completed quando exigido;
- rollback disponível mesmo após expiração.

P2 — Integração
O gate é aplicado em:
- Git create branch;
- Git write file/commit;
- Git open PR;
- Admin Evolution create branch;
- Admin Evolution apply branch patch;
- Admin Evolution revert branch patch;
- Admin Evolution merge PR.

ATIVAÇÃO EM DUAS FASES

Fase 1 — observe-only
EVOLUTION_MUTATION_AUTHORITY_REQUIRED=false

Nessa fase:
- o gate registra decisão legacy_mode;
- o fluxo atual não é quebrado;
- o hotfix de schema direto já está ativo.

Fase 2 — enforcement
EVOLUTION_MUTATION_AUTHORITY_REQUIRED=true

Habilitar somente as ações necessárias durante uma janela aprovada:
EVOLUTION_ALLOW_CREATE_BRANCH=true
EVOLUTION_ALLOW_WRITE_FILE=true
EVOLUTION_ALLOW_OPEN_PR=true
EVOLUTION_ALLOW_MERGE_PR=true

Manter:
EVOLUTION_ALLOW_DIRECT_SCHEMA=false
EVOLUTION_ALLOW_DEPLOY=false

IMPORTANTE
Na V1, approval_id é um alias de proposal_id porque o banco atual não possui
uma entidade imutável separada de aprovação. Isso é intencional para evitar uma
migration destrutiva no hotfix. A V2 deverá criar EvolutionApproval com:
- approval_id;
- proposal_id;
- actions_allowed;
- target_scope;
- issued_by;
- issued_at;
- expires_at;
- revoked_at.

VALIDAÇÃO
python -m pytest -q tests/test_ega005_mutation_authority.py

Resultado obtido:
5 passed

CHECKLIST PÓS-DEPLOY
[ ] trigger-health mostra auto_schema_hotfix_direct=false
[ ] erro de schema não executa SQL
[ ] observe-only não quebra Admin Evolution Center
[ ] branch create retorna mutation_authority
[ ] approval expirada é bloqueada em enforcement
[ ] dry run ausente é bloqueado
[ ] merge sem EVOLUTION_ALLOW_MERGE_PR é bloqueado
[ ] rollback continua autorizado
[ ] deploy permanece bloqueado
[ ] main direct permanece bloqueada

ROLLBACK
1. Restaurar main.py, evolution_trigger.py e git_internal.py.
2. Remover evolution_os/governance.
3. Remover as variáveis EGA-005.
4. Manter AUTO_SCHEMA_HOTFIX_DIRECT=false mesmo após rollback.

VEREDITO
GO CONTROLADO para deploy em observe-only.
NO-GO para enforcement total antes dos smoke tests do painel e dos endpoints.
