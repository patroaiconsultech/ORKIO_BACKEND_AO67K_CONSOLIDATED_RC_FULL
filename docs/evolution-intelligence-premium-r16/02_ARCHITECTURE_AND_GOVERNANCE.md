# Architecture and governance

## Authority chain

```text
observed platform signals
→ formal KPI registry
→ tenant-specific targets
→ health preview
→ diagnostics
→ transparent priorities
→ proposal-only preview
→ human decision
```

No stage in this release performs code mutation or proposal application.

## Runtime governance identity

`GET /api/admin/evolution/intelligence/runtime` exposes the active governance
identity and compares the current configuration with the validated boot state.

Relevant fields include:

```text
evolution_center_enabled
proposal_only
write_enabled
auto_apply_enabled
config_write_enabled
health_snapshot_write_enabled
proposal_generation_enabled
human_approval_required
rollback_required
governance_validated
governance_consistent
kpi_registry_version
```

An unsafe write or auto-apply configuration fails the application startup.

## KPI provenance

Each KPI definition declares:

```text
collector_version
source_version
time_window
aggregation
minimum_sample_size
freshness_seconds
confidence_method
failure_domain
```

Each health preview and captured snapshot carries the collection provenance
required to distinguish current evidence from stale or unknown evidence.

## Immutability model

The following tables are append-only at database level:

```text
evolution_health_snapshots
evolution_health_snapshot_provenance
evolution_health_snapshot_events
```

Update and delete operations are rejected by PostgreSQL and SQLite triggers.
Invalidation is represented by a new event, not by editing or deleting the
original snapshot.

## Versioned targets

The current target remains in `evolution_kpi_targets`. Every approved change
also appends an immutable historical row to
`evolution_kpi_target_versions`, with:

```text
version
effective_from
effective_to
changed_by
change_reason
approval_id
```
