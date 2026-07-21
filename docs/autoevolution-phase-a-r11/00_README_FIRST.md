# ORKIO Autoevolution Phase A R1.1

## Status

`proposal_only` — pacote rebaseado sobre o backend completo `(46)`.

Este pacote **não executa** commit, merge, deploy, migration ou alteração de flags.

## Baseline analisada

```text
artifact=ORKIO_BACKEND_AO67K_CONSOLIDATED_RC_FULL-main (46).zip
artifact_sha256=c7996f126c570254d1efc73cff23194414ed2f48866270ac41d64999fb131870
main_sha256=7a25bfd0538ce8ff180ee6916b43cc5bfe59891d24cc5f77da96c1aca7b20ab9
migration_code_head=0038_patch_auth_password_reset_tokens
branch=NOT_PROVEN
HEAD=NOT_PROVEN
deployed_commit=NOT_PROVEN
```

## Candidato

```text
patch_id=ORKIO-AUTOEVOLUTION-PHASE-A-R1.1
candidate_main_sha256=03a60be6fb48740edbecba266e934d049324256af390acd9ed83c4e2dea06f1c
release_identity_contract=ORKIO-REL-ID-R1.1
runtime_route_count_local=252
migration_added=false
frontend_changed=false
```

## Escopo

1. Rebase cirúrgico do EA-TENANT-R1.1 sobre a baseline `(46)`.
2. Preservação exata dos fluxos atuais de:
   - `register`;
   - `login`;
   - `forgot_password`;
   - `reset_password`;
   - `change_password`;
   - `_startup_access_gate_guard`;
   - migration `0038_patch_auth_password_reset_tokens`.
3. Tenant canônico em todas as rotas `/api/admin/evolution`.
4. Consultas e mutações por `proposal_id + org_slug`.
5. Remoção de fallback em memória para leituras/mutações administrativas sensíveis.
6. Estado precondicionado em approve/reject para impedir dupla transição concorrente.
7. Nova rota administrativa:
   - `GET /api/admin/system/version`
8. Identidade correlacionável:
   - commit;
   - branch;
   - deployment;
   - SHA do `main.py`;
   - heads Alembic do código;
   - revision Alembic do banco;
   - `migration_in_sync`;
   - tenant autenticado;
   - escopo de autoridade;
   - flags de governança.
9. Aplicador com preflight completo, `os.replace`, restauração integral e verificação pós-rollback.
10. Testes PostgreSQL com dois tenants incluídos, mas ainda não executados neste ambiente.

## Aplicação controlada

Dry-run:

```bash
python tools/apply_phase_a_r11.py /caminho/do/backend --dry-run
```

Aplicação local somente após aprovação:

```bash
python tools/apply_phase_a_r11.py /caminho/do/backend
```

O aplicador aceita somente:

```text
main_sha256=7a25bfd0538ce8ff180ee6916b43cc5bfe59891d24cc5f77da96c1aca7b20ab9
```

Qualquer outra baseline falha fechado.

## Flags

Manter:

```env
EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED=true
EVOLUTION_MARCO_ZERO_WRITE_ENABLED=false
EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED=false
EVOLUTION_AGENT_EVAL_WRITE_ENABLED=false
```

## Limitação bloqueante

O teste PostgreSQL real exige:

```text
ORKIO_TEST_POSTGRES_URL
```

Até que o teste com `tenant-a` e `tenant-b` passe:

```text
GO_DEPLOY=NO
GO_ENABLE_EVOLUTION_WRITE=NO
GO_MZ001_R2=HOLD
```
