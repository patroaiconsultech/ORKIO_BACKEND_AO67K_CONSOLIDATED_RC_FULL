# Rollback R1.4

## Código

Antes da aplicação:

```bash
git tag pre-premium-r14
```

Rollback preferencial após commit compartilhado:

```bash
git revert <commit-premium-r14>
git push
```

## Banco

A R1.4 não adiciona migration funcional.

A normalização controlada pode:

```text
criar alembic_version(version_num VARCHAR(128) NOT NULL)
ampliar version_num para VARCHAR(128)
```

O rollback de código não desfaz esse DDL. A ampliação para VARCHAR(128) é
compatível com revisions curtas e longas e não deve ser reduzida
automaticamente.

Se `alembic upgrade head` aplicar migrations funcionais existentes, o rollback
dessas migrations depende dos respectivos `downgrade()` e de aprovação humana.

## Critério de recuperação

```text
commit saudável identificado
Application startup complete
runtime_identity_status=validated
migration_database_status=ok
tenant isolation preservado
SSE terminal preservado
```
