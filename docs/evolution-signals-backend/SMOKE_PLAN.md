# Smoke readonly

## Saúde

```text
GET /api/health = 200
```

## Admin

```text
GET /api/admin/evolution/signals/current = 200
GET /api/admin/evolution/signals/history = 200
write_executed=false
```

## Segurança

```text
sem token = 401
não-admin = 403
tenant divergente = 403
```

## Prova de ausência de escrita

Registrar contagens antes e depois dos dois GETs:

```sql
SELECT COUNT(*) FROM platform_evolution_metric_snapshots;
SELECT COUNT(*) FROM agent_capability_evaluations;
```

Esperado:

```text
snapshot_count_delta=0
evaluation_count_delta=0
```

## POSTs bloqueados

```text
POST /api/admin/evolution/signals/snapshots/capture = 403
POST /api/admin/evolution/agent-evaluations = 403
```
