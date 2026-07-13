# OEC005 — Auth and Thread Visibility Tenant Diagnostic

## Status

```text
audit_report=true
issue_map=true
diagnostic_pack=true
write_executed=false
commit_executed=false
merge_executed=false
deploy_executed=false
migration_executed=false
human_approval_required=true
```

## Symptoms

1. The test account receives `401 Invalid credentials`.
2. The authenticated admin receives `200` from `/api/threads`, but no threads appear in the sidebar.

## Evidence from the current artifacts

- The frontend authentication page fixes `tenant` to `public`.
- Login resolves the user by both `User.org_slug == org` and normalized email.
- The same 401 response covers user-not-found and password mismatch.
- Admin thread visibility queries only `Thread.org_slug == resolved tenant`.
- Existing deployment logs contain both login 401 and login 200 responses.
- `/api/threads` repeatedly returned 200, but the logs do not record the response count.
- The deployed logs do not contain sufficient `LOGIN_USER_NOT_FOUND`,
  `LOGIN_PASSWORD_MISMATCH`, or tenant-inventory telemetry.

## Diagnostic implementation

This pack intentionally does not import `app.db` or `app.models`, because importing
`app.db` executes schema reconciliation routines. The diagnostic creates its own
SQLAlchemy connection and explicitly starts a read-only transaction.

Files:

```text
services/tenant_inventory_service.py
scripts/diagnose_tenant_drift.py
scripts/sql/oec005_tenant_inventory_readonly.sql
tests/test_tenant_inventory_service.py
```

## Railway execution

From the backend repository root:

```bash
PYTHONPATH=. python scripts/diagnose_tenant_drift.py \
  --current-tenant public \
  --email 'TESTER_EMAIL' \
  --email 'ADMIN_EMAIL' \
  --output /tmp/oec005_tenant_inventory.json
```

The output redacts emails as SHA-256 references and does not output passwords,
salts, password hashes, tokens or database credentials.

## Decision table

### Tenant drift likely

```text
tester account org_slug != public
or
public contains zero historical threads while another tenant contains them
```

Next action: create a governed recovery preview. Do not move data yet.

### Password issue likely

```text
tester account exists in public
+
approved=true
+
threads/users are aligned in public
```

Next action: reset the tester password through the approved auth flow and improve
login diagnostics.

### Data consistency risk

Any mismatch between thread, message, membership or user tenants blocks recovery
until an atomic repair plan and rollback are approved.

## Prohibited actions

- changing `DEFAULT_TENANT` blindly;
- global cross-tenant visibility for admin;
- moving only threads without messages and memberships;
- writing during `/api/threads`;
- logging raw email, password, salt, password hash, JWT or API key.


## V1.1 hardening

The diagnostic pack was hardened after independent review:

- `DATABASE_URL` is preferred inside Railway before public database URLs;
- the script verifies `current_setting('transaction_read_only')` and refuses execution
  unless the value is `on` or `true`;
- `user_id` is no longer included in the shareable report and is represented by a
  SHA-256 reference;
- `database_user` is no longer included in the shareable report;
- the verdict remains conservative when the same email exists in multiple tenants.

These changes do not authorize recovery, migration or any data write.
