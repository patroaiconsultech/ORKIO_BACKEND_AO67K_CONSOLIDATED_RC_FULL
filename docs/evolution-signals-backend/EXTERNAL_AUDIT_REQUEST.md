# Pedido de auditoria externa

Comparar este pacote com o `origin/main` atual.

## Baseline

```text
repository
branch
HEAD
origin/main
artifact_source
deployed_commit
runtime_import_path
```

## Validações obrigatórias

```text
main_diff_added_lines=16
main_diff_removed_lines=0
py_compile=PASS
focused_tests=16_pass
runtime_import=PASS
route_delta=+4
alembic_single_head=PASS
tenant_isolation=PASS
admin_only=PASS
GET_write_free=PASS
POST_default_disabled=PASS
migration_upgrade=PASS
migration_downgrade=PASS
secret_scan=PASS
```

## Baseline amplo reproduzido neste ambiente

Produção `(41)` sem patch:

```text
186 passed
8 failed
1 deselected
```

Produção `(41)` com patch cirúrgico:

```text
195 passed
8 failed
1 deselected
```

As oito falhas são as mesmas nos dois cenários. Portanto:

```text
new_regressions=false
```

Não classificar automaticamente essas oito falhas como aceitáveis para produção geral; elas apenas não foram introduzidas por este patch.
