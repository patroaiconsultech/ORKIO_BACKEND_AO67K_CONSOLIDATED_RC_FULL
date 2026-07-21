# ORKIO Backend Premium R1.4 — leia primeiro

Este pacote substitui integralmente o R1.3 antes de qualquer upload ou deploy.

## Escopo

A R1.4 preserva o `main.py` e o `runtime/release_identity.py` validados na
R1.3 e endurece exclusivamente a governança do boot e das migrations:

1. o primeiro acesso ao banco é readonly;
2. produção exige `ALLOW_AUTOMATIC_MIGRATIONS` explícito;
3. a tabela `alembic_version` só pode sofrer DDL com
   `ALLOW_ALEMBIC_VERSION_NORMALIZATION=true`;
4. o plano readonly roda antes de qualquer normalização ou `alembic upgrade`;
5. nenhum arquivo de migration funcional foi alterado ou adicionado.

## Estrutura

Extraia o conteúdo diretamente na raiz do backend. Não há pasta-wrapper.

## Decisão

```text
GO_BRANCH=GO
GO_PR=GO
GO_STAGING=GO_CONDITIONAL
GO_PRODUCTION=NO-GO_UNTIL_REAL_SMOKES
GO_EVOLUTION_WRITES=NO-GO
```
