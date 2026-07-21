# Segurança e identidade de release

## Rota

```text
GET /api/admin/system/version
```

Proteções:

```text
require_admin_access
get_request_org
X-Org-Slug divergente -> 403
```

A resposta inclui apenas metadados sanitizados.

## Campos

```text
contract_version
release_id
app_version
environment
commit_sha
branch
deployment_id
build_timestamp
migration_code_heads
migration_database_revisions
migration_database_revision
migration_database_status
migration_in_sync
route_count
runtime_main_path
runtime_main_sha256
authenticated_org
authority_scope
governance_flags
```

## Auditoria

O acesso gera log estruturado:

```text
ADMIN_SYSTEM_VERSION_ACCESSED
request_id=
actor_ref=
org=
authority_scope=
status_code=200
migration_in_sync=
```

`actor_ref` é hash truncado. Não são registrados e-mail bruto, token, cookie, senha, API key ou `DATABASE_URL`.

## Readonly

A rota não grava auditoria no banco. Isso preserva o contrato readonly. A trilha é observacional via log estruturado.
