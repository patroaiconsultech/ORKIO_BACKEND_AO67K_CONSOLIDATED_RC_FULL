# Pedido de auditoria externa

Auditar o pacote sem commit, merge, deploy, migration ou escrita em produção.

## Perguntas

1. O rebase preserva integralmente auth/reset e os gates de login/cadastro?
2. Todas as rotas `/api/admin/evolution` usam tenant canônico?
3. Toda consulta/mutação por proposta inclui `org_slug`?
4. O fallback em memória foi removido dos caminhos sensíveis?
5. A precondição de status evita dupla aprovação?
6. A identidade diferencia Alembic do código e do banco?
7. A rota de versão é tenant-scoped e não expõe segredos?
8. O aplicador restaura todos os arquivos em falha?
9. O manifesto cobre todas as entradas do ZIP?
10. Os nomes das falhas da suíte permanecem iguais à baseline?

## Saída

```text
BASELINE_MATCH=
AUTH_REGRESSION=
TENANT_BOUNDARY=
FOREIGN_PROPOSAL=
CONCURRENCY=
RELEASE_IDENTITY=
DATABASE_REVISION_IDENTITY=
APPLIER_ROLLBACK=
MANIFEST_COMPLETENESS=
NEW_REGRESSIONS=
READY_FOR_POSTGRES_CI=
READY_FOR_DEPLOY=
```

Veredito esperado nesta etapa:

```text
GO_POSTGRES_CI=CONDITIONAL
GO_DEPLOY=NO
GO_ENABLE_WRITE=NO
```
