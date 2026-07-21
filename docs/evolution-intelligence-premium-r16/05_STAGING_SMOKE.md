# Staging smoke plan

## 1. Correlate the artifact

Record:

```text
repository
branch
commit
deployment_id
runtime_main_sha256
migration_code_heads
migration_database_revisions
```

## 2. Boot

Expected logs:

```text
PYTHON_NAMESPACE_PREFLIGHT_OK
ORKIO_BOOT_IDENTITY
EVOLUTION_INTELLIGENCE_GOVERNANCE_OK
Application startup complete
```

Unsafe configuration must fail closed:

```env
EVOLUTION_WRITE_ENABLED=true
```

Expected result:

```text
EVOLUTION_GOVERNANCE_INVALID
startup blocked
```

## 3. Migrations

Confirm:

```text
current=0040_patch_evolution_intelligence_premium_lineage
heads=0040_patch_evolution_intelligence_premium_lineage
migration_in_sync=true
```

Inspect the six Evolution Intelligence tables and immutable triggers.

## 4. Tenant isolation

Use two real tenants.

For each resource type:

```text
objective
target
target history
snapshot
snapshot provenance
invalidation event
audit
```

Tenant B must not read, update or invalidate tenant A records.

## 5. Runtime governance identity

Call:

```text
GET /api/admin/evolution/intelligence/runtime
```

Require:

```text
governance_validated=true
governance_consistent=true
write_enabled=false
auto_apply_enabled=false
proposal_only=true
```

## 6. Provenance and immutable snapshot

1. Capture one approved snapshot with snapshot write explicitly enabled.
2. Confirm collector/source versions, window bounds, sample size and hash.
3. Attempt direct UPDATE and DELETE in a controlled transaction.
4. Both must fail with `ORKIO_IMMUTABLE_RECORD`.
5. Invalidate through the API.
6. Confirm the original snapshot is unchanged and a new event exists.

## 7. Versioned targets

Create two approved versions of one target.

Confirm:

```text
version 1 effective_to is closed
version 2 effective_to is null
change_reason recorded
approval_id recorded
changed_by recorded
```

## 8. Platform regression smoke

The release does not change SSE, ownership or auth, but production promotion
still requires:

```text
login and reset password
thread visibility
cross-tenant block
selected-agent ownership
SSE success → done
SSE error → error + done
assistant persistence
input release
```
