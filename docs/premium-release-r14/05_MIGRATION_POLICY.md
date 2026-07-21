# Política de migrations R1.4

## Separação de autoridades

```text
ALLOW_AUTOMATIC_MIGRATIONS
  autoriza ou bloqueia alembic upgrade head

ALLOW_ALEMBIC_VERSION_NORMALIZATION
  autoriza ou bloqueia DDL limitado à tabela alembic_version
```

Uma flag não autoriza a outra.

## Produção

`ALLOW_AUTOMATIC_MIGRATIONS` é obrigatória em produção. Ausência bloqueia o
boot, mesmo quando o banco parece sincronizado.

`ALLOW_ALEMBIC_VERSION_NORMALIZATION` possui default false. Quando nenhuma
normalização é necessária, o boot segue em readonly no-op.

## Estado estacionário recomendado

```env
ALLOW_AUTOMATIC_MIGRATIONS=false
ALLOW_ALEMBIC_VERSION_NORMALIZATION=false
```

## Janela controlada

```text
preview readonly
→ aprovação humana
→ backup/rollback
→ flag específica true
→ deploy controlado
→ migration_in_sync=true
→ flag false
```

## Garantias

O primeiro script com acesso ao banco é readonly e não contém DDL. Revisões
desconhecidas e múltiplos code heads bloqueiam independentemente das flags.
