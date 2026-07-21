# ORKIO Backend — Access Grant Header Bridge R1.7

## Objetivo

Eliminar a dependência exclusiva de cookie cross-site no cadastro, sem
desligar o Access Gate.

## Fluxo

```text
POST /api/access-grants/validate
→ grant assinado curto

POST /api/auth/register
X-ORKIO-Access-Grant: <grant>
→ backend valida assinatura, tenant, expiração, user-agent e code_id
```

O cookie HttpOnly continua existindo. O header é um fallback explícito para
navegadores que bloqueiam cookies de terceiros.

## ENV obrigatória

```env
ACCESS_GATE_HEADER_TRANSPORT_ENABLED=true
```

## Segurança

O grant:

- é assinado com `ACCESS_GATE_SIGNING_KEY`;
- expira;
- é tenant-scoped;
- pode ser vinculado ao user-agent;
- não deve ser persistido no browser;
- não substitui a validação do `SignupCode`.

## Rollback

```env
ACCESS_GATE_HEADER_TRANSPORT_ENABLED=false
```
