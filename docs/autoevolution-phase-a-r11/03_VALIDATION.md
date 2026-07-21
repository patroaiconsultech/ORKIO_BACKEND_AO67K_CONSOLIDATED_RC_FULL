# Validação executada

## Sintaxe e integridade

```text
py_compile=PASS
changed_python_files=11
three_way_rebase=CLEAN
conflict_markers=0
secret_scan=PASS
git_diff_check=PASS
```

## Testes focais

```text
passed=34
failed=0
skipped=2
```

Os dois skips pertencem aos testes PostgreSQL condicionais.

## Suíte completa

Baseline `(46)`:

```text
228 passed
8 failed
2 skipped
```

Candidato R1.1:

```text
262 passed
8 failed
4 skipped
```

```text
failure_names_match_baseline=true
new_regressions=false
```

As oito falhas preexistentes permanecem nas famílias AO-01 e DOCIO/document artifacts. Elas não foram mascaradas nem modificadas por este pacote.

## Runtime local

```text
runtime_import=PASS
baseline_route_count=251
candidate_route_count=252
release_route_present=true
migration_code_head=0038_patch_auth_password_reset_tokens
tenant_canary_present=true
```

## PostgreSQL

```text
postgres_two_tenant_test=NOT_EXECUTED
reason=ORKIO_TEST_POSTGRES_URL unavailable
```

Os testes estão incluídos e cobrem:

- leitura cross-tenant;
- mutação cross-tenant;
- delta zero;
- header mismatch;
- duas aprovações concorrentes com um único vencedor.

## Aplicador contra a baseline `(46)`

```text
package_dry_run=PASS
simulated_failure_after=3
rollback_exact=true
disposable_copy_apply=PASS
all_payload_hashes_match=true
second_apply=already_applied
```
