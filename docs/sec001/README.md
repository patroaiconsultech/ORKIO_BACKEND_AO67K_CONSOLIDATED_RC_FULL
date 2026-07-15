# SEC-001 — Server-Side Access Gate & Environment Hardening

## Scope

This patch moves private access-code validation out of the public Vite bundle and
into the FastAPI backend. It also makes evolution mutation authority fail-closed.

## Security contract

- No access-code allowlist in React/Vite.
- No `VITE_*` secret/code variable.
- No query-string bypass.
- No raw access code in localStorage/sessionStorage.
- Signup codes remain SHA-256 hashes in PostgreSQL.
- Access grants are HMAC-signed, HttpOnly, Secure and tenant-bound.
- Validation attempts are rate-limited and audited.
- PostgreSQL advisory locking serializes attempts across replicas.
- Login/registration enforcement is activated only after staged rollout.
- Browser API calls stay same-origin through `/api` when `USE_API_PROXY=true`.

## New backend endpoints

- `POST /api/access-grants/validate`
- `GET /api/access-grants/status`
- `POST /api/access-grants/revoke`

## Rollout

1. Backend Stage 1: deploy with `ACCESS_GATE_REQUIRE_FOR_AUTH=false`.
2. Create new governed signup codes through `/api/admin/summit/codes`.
3. Validate grant/status through the frontend domain.
4. Deploy the frontend without client-side codes.
5. Backend Stage 2: set `ACCESS_GATE_REQUIRE_FOR_AUTH=true`.
6. Revoke old codes and inspect the public bundle.

## Rollback

- Set `ACCESS_GATE_REQUIRE_FOR_AUTH=false` to restore login/register while
  keeping server-side validation available.
- Do not restore retired client-side codes.
- Do not restore compromised credentials.
