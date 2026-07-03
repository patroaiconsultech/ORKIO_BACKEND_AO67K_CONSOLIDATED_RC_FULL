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
