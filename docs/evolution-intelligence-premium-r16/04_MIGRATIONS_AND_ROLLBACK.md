# Migrations and rollback

## Upgrade chain

The cumulative package must be applied over R1.4:

```text
0038_patch_auth_password_reset_tokens
→ 0039_patch_evolution_intelligence_foundation
→ 0040_patch_evolution_intelligence_premium_lineage
```

### Migration 0039

Creates:

```text
evolution_objectives
evolution_kpi_targets
evolution_health_snapshots
```

### Migration 0040

Creates:

```text
evolution_kpi_target_versions
evolution_health_snapshot_provenance
evolution_health_snapshot_events
```

It also creates immutable mutation guards for snapshots, provenance and events.

## Migration governance

The R1.4 boot contract remains in force:

```text
preflight_migration_plan.py
→ preflight_alembic_version.py
→ alembic upgrade head
```

Use explicit environment values in staging:

```env
ALLOW_AUTOMATIC_MIGRATIONS=true
ALLOW_ALEMBIC_VERSION_NORMALIZATION=true
```

After confirming synchronization and the Alembic control column length:

```env
ALLOW_AUTOMATIC_MIGRATIONS=false
ALLOW_ALEMBIC_VERSION_NORMALIZATION=false
```

## Code rollback

```bash
git revert <r16-commit>
```

## Database rollback

When no R1.6 data must be preserved:

```bash
alembic downgrade 0038_patch_auth_password_reset_tokens
```

A staged rollback can first remove only R1.6 lineage:

```bash
alembic downgrade 0039_patch_evolution_intelligence_foundation
```

Before downgrade, export objectives, targets, target history, snapshots,
provenance and invalidation events.

Code rollback alone does not revert database changes.
