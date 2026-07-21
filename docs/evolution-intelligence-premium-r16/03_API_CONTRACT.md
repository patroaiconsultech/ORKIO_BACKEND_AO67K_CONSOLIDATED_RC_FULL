# Administrative API contract

Prefix:

```text
/api/admin/evolution/intelligence
```

All routes require administrative access and canonical tenant resolution.

## Read routes

```text
GET /runtime
GET /inventory
GET /objectives
GET /objectives/{objective_id}
GET /kpis
GET /kpis/{kpi_code}
GET /targets/history
GET /health/preview
GET /diagnostics/preview
GET /priorities/preview
GET /health/snapshots
GET /health/snapshots/events
GET /audit
```

## Controlled write routes

```text
POST  /objectives
PATCH /objectives/{objective_id}
PUT   /targets
POST  /health/snapshots/capture
POST  /health/snapshots/{snapshot_id}/invalidate
```

Controlled writes require:

```text
approved=true
admin authentication
canonical tenant
corresponding feature flag
human_approval_required=true
audit event
```

`PUT /targets` additionally requires:

```text
change_reason
approval_id
```

## Proposal preview

```text
POST /proposals/preview
```

The response remains:

```text
mode=proposal_only
auto_apply=false
write_executed=false
human_approval_required=true
```

No diff is fabricated when root cause is not confirmed.
