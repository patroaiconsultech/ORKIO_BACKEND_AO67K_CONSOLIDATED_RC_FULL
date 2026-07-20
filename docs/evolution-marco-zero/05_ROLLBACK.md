# Rollback

## R1

Não há migration nem escrita.

Rollback:

```text
EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED=false
reverter commit
redeploy
```

## R2 futuro

O rollback será lógico e vinculado ao `baseline_id`.

Proibido:

```text
DELETE físico
SQL manual sem preview
restauração cross-tenant
restauração sem inventário
```
