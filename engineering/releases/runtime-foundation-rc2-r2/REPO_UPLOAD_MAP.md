# ORKIO Backend Upload Map — Runtime Foundation RC2-R2

Este pacote está organizado para ser aplicado na **raiz do repositório backend** em branch dedicada.

## Diretórios aplicados na raiz

- `runtime/`
- `tests/`
- `tools/`
- `adrs/`
- `architecture/`
- `engineering/`

## Documentação da release

Toda a documentação consolidada da release foi colocada em:

`engineering/releases/runtime-foundation-rc2-r2/`

Isso evita sobrescrever o `README.md` oficial do backend.

## Regras de aplicação

- Não aplicar direto na `main`.
- Usar branch dedicada, por exemplo: `release/runtime-foundation-rc2-r2`.
- Não promover para `guarded`, enforcement ou produção sem nova auditoria independente.
- O aplicador exige o baseline SHA oficial:
  `94ba9246bcd3d2a5c40d42657ae7ca17c80a2826`

## Comando sugerido após upload

```bash
python tools/apply_shadow_candidate.py --check
python tools/apply_shadow_candidate.py --write
python tools/validate_shadow_candidate.py
pytest -p no:cacheprovider tests/test_rc2_shadow_candidate_sha_guard.py
pytest -p no:cacheprovider tests/runtime/test_runtime_persistence_shadow.py
```


## AO-01 R1 Repo-Ready Correction

This repo-ready artifact is intended to be extracted into the backend repository
root BEFORE the upload commit is created.

Required order:

1. Checkout the locked baseline commit:
   `94ba9246bcd3d2a5c40d42657ae7ca17c80a2826`
2. Create a branch from that commit.
3. Extract this ZIP into the repository root.
4. Run: `python tools/apply_shadow_candidate.py --check`
5. Run: `python tools/apply_shadow_candidate.py --write`
6. Run the same write command again to confirm idempotence.
7. Run: `python tools/validate_shadow_candidate.py`
8. Run: `pytest -p no:cacheprovider tests/runtime tests/repository`
9. Commit only after the validation above passes.

Do not commit the extracted files before running the applier, because the SHA
guard intentionally requires HEAD to remain at the locked baseline.
