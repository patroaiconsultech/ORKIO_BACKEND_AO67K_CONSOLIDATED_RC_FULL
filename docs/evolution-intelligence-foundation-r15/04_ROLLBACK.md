# Rollback

## Código

Reverter o commit da R1.5:

```bash
git revert <commit-r15>
```

## Flags imediatas

```env
EVOLUTION_CENTER_ENABLED=false
EVOLUTION_CONFIG_WRITE_ENABLED=false
EVOLUTION_HEALTH_SNAPSHOT_WRITE_ENABLED=false
EVOLUTION_PROPOSAL_GENERATION_ENABLED=false
EVOLUTION_WRITE_ENABLED=false
EVOLUTION_AUTO_APPLY_ENABLED=false
```

## Banco

A migration adiciona somente três tabelas novas.

Antes do downgrade:

1. exportar snapshots e objetivos;
2. confirmar que nenhuma rota ainda usa as tabelas;
3. executar em staging primeiro.

Downgrade:

```bash
alembic downgrade 0038_patch_auth_password_reset_tokens
```

O rollback de código não desfaz automaticamente o banco.

## Critério de abortar staging

Abortar se ocorrer:

- tenant leak;
- migration inconsistente;
- startup governance failed;
- release identity inconsistente;
- falso verde com fonte ausente;
- proposal preview com `auto_apply=true`;
- qualquer escrita com flags desabilitadas.
