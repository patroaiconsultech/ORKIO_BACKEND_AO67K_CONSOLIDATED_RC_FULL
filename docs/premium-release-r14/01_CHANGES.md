# Alterações R1.4

## Bloqueador corrigido

Na R1.3, `preflight_alembic_version.py` executava `CREATE TABLE` e `ALTER
TABLE` antes do gate de migrations. A R1.4 inverte a ordem e separa inspeção de
mutação.

## Nova ordem de boot

```text
preflight_migration_plan.py          # readonly e policy gate
preflight_alembic_version.py         # readonly; DDL somente se autorizado
alembic upgrade head                 # somente após os dois gates
preflight_python_namespace.py
uvicorn app.main:app
```

## Políticas

### Aplicação de migrations

- produção sem `ALLOW_AUTOMATIC_MIGRATIONS`: bloqueia;
- produção com `false` e banco sincronizado: continua;
- produção com `false` e migration pendente: bloqueia;
- `true`: permite migration conhecida, desde que não haja revision desconhecida
  ou múltiplos code heads;
- fora de produção, ausência preserva o legado `true`, explicitamente marcada
  como `nonproduction_legacy_default_true`.

### Normalização da tabela de controle

- default: `false`;
- sem necessidade de normalização: readonly no-op;
- normalização necessária e flag ausente/false: bloqueia sem DDL;
- normalização necessária e flag true: permite apenas criar
  `alembic_version` em VARCHAR(128) ou ampliar `version_num` para VARCHAR(128);
- schema inválido sem `version_num`: bloqueia.

## Arquivos funcionais alterados

```text
Dockerfile
scripts/preflight_migration_plan.py
scripts/preflight_alembic_version.py
scripts/validate_premium_package.py
tests/test_migration_plan_governance.py
tests/test_alembic_version_normalization_governance.py
```

`main.py`, `runtime/release_identity.py` e migrations funcionais não foram
alterados em relação à R1.3.
