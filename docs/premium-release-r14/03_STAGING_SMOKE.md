# Plano de staging e smoke R1.4

## 1. Branch

```bash
git checkout main
git pull
git rev-parse HEAD
git checkout -b premium-r14-readonly-migration-gate
```

Extraia o ZIP diretamente na raiz e execute:

```bash
python scripts/validate_premium_package.py
python -m py_compile main.py runtime/release_identity.py   scripts/preflight_migration_plan.py   scripts/preflight_alembic_version.py

pytest -q   tests/test_python_namespace_contract.py   tests/test_release_identity_premium_contract.py   tests/test_release_identity_module_fallback_parity.py   tests/test_release_identity_r11_route.py   tests/test_ao01_single_route_authority.py   tests/test_migration_plan_governance.py   tests/test_alembic_version_normalization_governance.py
```

## 2. Variáveis do primeiro staging

Para staging controlado que poderá aplicar migrations e corrigir a tabela de
controle:

```env
ALLOW_AUTOMATIC_MIGRATIONS=true
ALLOW_ALEMBIC_VERSION_NORMALIZATION=true
```

Depois de comprovar `migration_in_sync=true` e `current_length=128`, alterar:

```env
ALLOW_AUTOMATIC_MIGRATIONS=false
ALLOW_ALEMBIC_VERSION_NORMALIZATION=false
```

## 3. Logs obrigatórios

```text
ORKIO_MIGRATION_PLAN ... database_access_mode=readonly
ORKIO_MIGRATION_PLAN_OK access_mode=readonly
ORKIO_ALEMBIC_VERSION_PLAN ...
ALEMBIC_VERSION_PREFLIGHT_OK mode=readonly_noop|controlled_write
PYTHON_NAMESPACE_PREFLIGHT_OK
ORKIO_BOOT_IDENTITY
EVOLUTION_ADMIN_TENANT_GUARD_BOOT_OK
Application startup complete
```

Bloqueios válidos:

```text
automatic_migration_policy_not_explicit
pending_migrations_automatic_execution_disabled
unknown_database_revision
multiple_code_heads
normalization_required_but_not_allowed
alembic_version_missing_version_num
```

## 4. Release identity

```http
GET /api/admin/system/version
```

Exigir:

```text
commit_sha != unknown
deployment_id != unknown
migration_database_status=ok
migration_in_sync=true
runtime_identity_validated=true
runtime_identity_status=validated
runtime_identity_consistent=true
release_identity_source=runtime_module
boot_release_identity_source=runtime_module
write_flags=false
```

## 5. Smokes críticos

```text
admin=200
usuário comum=401|403
tenant divergente=403|404
cross_tenant delta=zero
login/reset/cadastro=PASS
SSE sucesso=done
SSE erro=error+done
SSE timeout=error+done
assistant_persisted=true
input_released=true
```

## 6. Produção

Produção deve declarar explicitamente:

```env
ALLOW_AUTOMATIC_MIGRATIONS=false
ALLOW_ALEMBIC_VERSION_NORMALIZATION=false
```

Uma janela aprovada de migration deve alterar temporariamente apenas a flag
necessária, registrar logs, validar `migration_in_sync=true` e retornar ambas
para `false`.
