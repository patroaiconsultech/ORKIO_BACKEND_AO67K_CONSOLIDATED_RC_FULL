# Contrato de API R1

Prefixo:

```text
/api/admin/evolution/intelligence
```

Todas as rotas exigem acesso administrativo e tenant canônico.

## Readonly

```http
GET /runtime
GET /inventory
GET /objectives
GET /objectives/{objective_id}
GET /kpis
GET /kpis/{kpi_code}
GET /health/preview
GET /diagnostics/preview
GET /priorities/preview
GET /health/snapshots
GET /audit
```

## Escritas de configuração

```http
POST  /objectives
PATCH /objectives/{objective_id}
PUT   /targets
```

Requisitos:

```text
EVOLUTION_CONFIG_WRITE_ENABLED=true
approved=true
human_approval_required=true
```

## Snapshot composto

```http
POST /health/snapshots/capture
```

Requisitos:

```text
EVOLUTION_HEALTH_SNAPSHOT_WRITE_ENABLED=true
approved=true
```

## Proposal preview

```http
POST /proposals/preview
```

Requisitos:

```text
EVOLUTION_PROPOSAL_GENERATION_ENABLED=true
EVOLUTION_PROPOSAL_ONLY=true
EVOLUTION_WRITE_ENABLED=false
EVOLUTION_AUTO_APPLY_ENABLED=false
```

O retorno sempre contém:

```text
mode=proposal_only
auto_apply=false
write_executed=false
```

Uma proposta técnica só é sugerida quando a confiança é pelo menos 0,85.
Mesmo assim, a causa raiz permanece `not_confirmed` até existir evidência.
