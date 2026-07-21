# Escopo técnico e primeira divergência

## Primeira divergência corrigida

Na baseline `(46)`, as rotas administrativas de Evolution ainda podiam:

- resolver tenant por `get_org(...)`;
- consultar proposta apenas por `proposal_id`;
- atualizar status sem `org_slug`;
- cair em memória quando PostgreSQL falhava.

O candidato altera apenas o domínio Evolution Admin e a observabilidade de release.

## Invariantes

```text
explicit_tenant_from_authenticated_identity=true
x_org_slug_mismatch=403
proposal_lookup=proposal_id+org_slug
proposal_update=proposal_id+org_slug
execution_queries=org_slug
database_failure=fail_closed
memory_fallback=false
marco_zero=preview_only
write_flags=false
```

## Concorrência

Approve/reject usa precondição:

```sql
WHERE proposal_id = :proposal_id
  AND org_slug = :org_slug
  AND LOWER(status) IN ('pending_approval', 'draft')
```

A primeira transição válida afeta uma linha. Uma segunda tentativa recebe `409`.

## Auth preservado

Os hashes de fonte das funções de autenticação foram congelados em teste de regressão. O pacote não reescreve o fluxo de senha nem a separação dos gates de login e cadastro.
