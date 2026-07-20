# Uso recomendado do Codex

Usar o Codex somente depois do backend estar implantado.

## Teste de usuário

1. Entrar como admin.
2. Abrir Evolution Center.
3. Clicar em `Preview marco zero`.
4. Confirmar mensagem de nenhuma escrita.
5. Comparar `candidate_count` com a lista.
6. Confirmar preview de no máximo 50 IDs.
7. Confirmar indicação de truncamento.
8. Testar usuário não-admin.
9. Testar tenant divergente.
10. Confirmar que não existe ação de aplicação real.

## Saída curta

```text
backend_canary=
preview_status=
candidate_count=
preview_ids=
preview_truncated=
write_executed=
database_delta=
non_admin_status=
tenant_mismatch_status=
browser_console_errors=
user_copy_clear=
```

O Codex não precisa redesenhar arquitetura nem gerar patch nesta fase.
