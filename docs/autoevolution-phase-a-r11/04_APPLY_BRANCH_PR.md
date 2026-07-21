# Aplicação, branch e PR

## Preflight

```bash
sha256sum main.py
python tools/apply_phase_a_r11.py . --dry-run
```

Esperado:

```text
observed_main_sha256=7a25bfd0538ce8ff180ee6916b43cc5bfe59891d24cc5f77da96c1aca7b20ab9
candidate_main_sha256=03a60be6fb48740edbecba266e934d049324256af390acd9ed83c4e2dea06f1c
mode=dry_run
write_executed=false
```

## Branch recomendada

```text
autoevolution-phase-a-r11
```

Commit sugerido somente após CI PostgreSQL verde:

```text
fix(evolution): rebase canonical tenant guard and release identity on auth-reset baseline
```

## Ordem

```text
dry-run
→ branch
→ aplicar localmente
→ py_compile
→ testes focais
→ PostgreSQL tenant-a/tenant-b
→ full pytest
→ diff review
→ PR
→ revisão humana
```

## Proibições

```text
merge_now=false
deploy_now=false
migration_execution=false
write_flag_change=false
production_cross_tenant_test=false
```
