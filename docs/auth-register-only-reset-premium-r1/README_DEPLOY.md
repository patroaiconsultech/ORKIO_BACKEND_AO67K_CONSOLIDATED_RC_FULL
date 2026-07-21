# ORKIO Auth Register-Only + Reset Premium R1

## Estado-alvo

- Cadastro novo: exige código especial.
- Login de conta existente: não exige código especial.
- Recuperação de senha: resposta pública genérica, token de uso único, observabilidade por estágio e revogação de todos os links após sucesso.

## Variáveis recomendadas

```env
ACCESS_GATE_SERVER_SIDE_ONLY=true
ACCESS_GATE_REQUIRE_FOR_REGISTER=true
ACCESS_GATE_REQUIRE_FOR_LOGIN=false
```

Compatibilidade temporária:

`ACCESS_GATE_REQUIRE_FOR_AUTH` continua existindo como fallback legado do cadastro.
O login permanece aberto por padrão, mesmo quando a flag legada estiver ativa.

## Frontend obrigatório

O componente que envolve a página de autenticação não deve bloquear:

- `mode=login`
- `mode=forgot`
- `mode=reset`

O gate deve ser mostrado apenas em:

- `mode=register`

Contrato recomendado:

```jsx
const authMode = new URLSearchParams(window.location.search).get("mode") || "login";
const requiresSpecialCode = authMode === "register";

if (!requiresSpecialCode) {
  return children;
}
```

O código especial continua sendo validado exclusivamente no backend.

## Logs esperados

```text
AUTH_ACCESS_GATE_DECISION route=login required=False
AUTH_ACCESS_GATE_DECISION route=register required=True
FORGOT_PASSWORD_REQUEST_RECEIVED
FORGOT_PASSWORD_TOKEN_PERSISTED
FORGOT_PASSWORD_PROVIDER_ACCEPTED
RESET_PASSWORD_COMPLETED ... all_tokens_revoked=true
```

## Rollback

- Reverter `main.py` e `services/access_grant_service.py`.
- Ou reativar temporariamente o login gate com:
  `ACCESS_GATE_REQUIRE_FOR_LOGIN=true`.
