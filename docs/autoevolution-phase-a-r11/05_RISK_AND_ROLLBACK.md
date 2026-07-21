# Riscos e rollback

## Riscos principais

1. Baseline diferente da `(46)`.
   - Mitigação: SHA exato e fail-closed.
2. Estado parcial durante cópia.
   - Mitigação: staging, escrita por `os.replace`, backup em memória e restauração integral.
3. Divergência Alembic código/banco.
   - Mitigação: `migration_code_heads`, `migration_database_revisions` e `migration_in_sync`.
4. Regressão de autenticação.
   - Mitigação: hashes de fonte das funções críticas e preservação da migration 0038.
5. Concorrência em approve/reject.
   - Mitigação: precondição de status e `rowcount == 1`.
6. Semântica PostgreSQL não reproduzida por SQLite.
   - Mitigação: testes PostgreSQL obrigatórios antes do PR ser aprovado.

## Rollback de aplicação local

O aplicador restaura todos os destinos se qualquer arquivo falhar.

## Rollback Git

```bash
git revert <commit-phase-a-r11>
```

ou, antes de merge:

```bash
git reset --hard <commit-anterior>
```

## Rollback de produção

- redeploy do commit anterior;
- manter todas as flags de escrita `false`;
- não há migration nova neste pacote;
- não há rollback de dados.
