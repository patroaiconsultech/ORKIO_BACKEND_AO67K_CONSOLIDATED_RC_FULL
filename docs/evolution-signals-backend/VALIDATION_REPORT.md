# Relatório de validação

```text
artifact_source=ORKIO_BACKEND_AO67K_CONSOLIDATED_RC_FULL-main (41).zip
artifact_sha256=855b0fe8c0b862f02727bd1a9c909195ea47c92b5f9f5c91d2ff6b1f45957ba6
artifact_integrity=PASS
artifact_entries=1050

main_before_sha256=35daf4bef0765b197f3c6def1633fd890da476fe5c0fe237a65537dd92485ea5
main_after_sha256=d9eb8b8c11f5b673808d6f01c3df48252e64b5f612b4675770c9fd7d6253177d
main_added_lines=16
main_removed_lines=0

py_compile=PASS
focused_tests=16 passed
runtime_import=PASS
runtime_route_count=249
route_delta=+4
alembic_head=0037_patch_evolution_signals_metrics

baseline_full_suite=186 passed, 8 failed, 1 deselected
candidate_full_suite=195 passed, 8 failed, 1 deselected
new_regressions=false

migration_executed=false
deploy_executed=false
commit_executed=false
merge_executed=false
human_approval_required=true
```

## Nota

A mensagem de warmup do `artifact_tool` observada no ambiente de teste é externa ao repositório ORKIO e não alterou o resultado do `py_compile` ou dos testes.
