# Plano de staging

## Ambiente

Usar PostgreSQL descartável ou staging isolado.

```bash
export ORKIO_TEST_POSTGRES_URL='[configurado fora de logs]'
pytest -q tests/test_evolution_admin_tenant_r11_postgres.py
```

Não imprimir a URL.

## Critérios

```text
tenant_a_reads_only_a=true
tenant_b_reads_only_b=true
header_mismatch=403
tenant_a_reads_proposal_b=404|403
tenant_a_approves_proposal_b=404|403
cross_tenant_proposal_delta=0
cross_tenant_execution_delta=0
concurrent_approval_successes=1
concurrent_approval_conflicts=1
```

## Smoke da rota de identidade

```text
GET /api/admin/system/version -> 200
authenticated_org=<tenant autenticado>
authority_scope=tenant_admin|platform_admin
commit_sha != unknown
deployment_id != unknown
runtime_main_sha256=<hash do artefato>
migration_in_sync=true
```

## Smoke Evolution

```text
GET proposals=200
GET executions=200
GET detail=200
GET execution-plan=200
POST archive-baseline?dry_run=true=200
dry_run=false=403
write_executed=false
```
