# Validation report

## Static and unit validation

```text
python_files_compiled=585
compile_errors=0
new_tests=20 passed
existing_evolution_tests=34 passed, 2 skipped
full_suite=316 passed, 7 failed, 4 skipped
new_failures=0
```

The seven failures are the same pre-existing R1.4 failures:

- 2 AO-01 route diagnostics;
- 3 DOCIO payload/bridge;
- 2 document artifact rendering.

## KPI and governance validation

```text
registry_version=ORKIO-EVOLUTION-KPI-REGISTRY-R1
registered_kpis=7
definition_complete=7
auto_apply_enabled=false
write_enabled=false
proposal_only=true
governance_validator=PASS
```

## Migration validation

```text
source_revision=0038_patch_auth_password_reset_tokens
target_revision=0039_patch_evolution_intelligence_foundation
sqlite_targeted_upgrade=PASS
tables_created=3
tenant_composite_fk=PASS
global_target_scope_unique=PASS
objective_name_tenant_unique=PASS
```

The targeted SQLite upgrade validates the 0038→0039 migration syntax and
constraints. The historical migration chain contains PostgreSQL-specific SQL,
so a full SQLite upgrade from revision zero is not a valid test. PostgreSQL
staging remains mandatory.

## Runtime validation

```text
app.main_import=PASS
fastapi_startup=PASS
evolution_intelligence_status=validated
runtime_identity_status=validated
health_http=200
route_count=268

unsafe_EVOLUTION_WRITE_ENABLED=true
startup=BLOCKED
error=EVOLUTION_GOVERNANCE_INVALID:code_write_not_allowed_in_foundation_r1
```

## Limitations

```text
real_postgresql=NOT_EXECUTED
railway=NOT_EXECUTED
two_tenant_postgresql=NOT_EXECUTED
live_sse_provider=NOT_EXECUTED
frontend=NOT_INCLUDED
deploy=NOT_EXECUTED
migration_executed_on_real_environment=NO
```
