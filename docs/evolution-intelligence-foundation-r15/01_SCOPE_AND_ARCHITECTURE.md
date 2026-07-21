# Escopo e arquitetura

## Estado anterior confirmado

A plataforma já possuía:

- `platform_evolution_metric_snapshots`;
- `agent_capability_evaluations`;
- `evolution_proposals`;
- `admin_evolution_proposals`;
- auditoria;
- rotas de sinais;
- governança proposal-only.

Duplicar essas estruturas criaria contratos concorrentes.

## Arquitetura escolhida

```text
sinais atuais
→ catálogo KPI versionado
→ metas por tenant/objetivo
→ health preview
→ diagnóstico
→ prioridade
→ proposal preview
→ aprovação humana futura
```

## Entidades novas

```text
evolution_objectives
evolution_kpi_targets
evolution_health_snapshots
```

Os snapshots individuais continuam usando
`platform_evolution_metric_snapshots`.

As propostas continuam usando os contratos governados existentes; esta fase
gera apenas previews não persistidos.

A auditoria continua usando `audit_logs`, filtrada pelo prefixo
`evolution_intelligence.`.

## Decisões de segurança

- `org_slug` em todas as consultas;
- referência composta de objetivo + tenant no banco;
- `scope_key` não nulo para impedir duplicidade de meta global no PostgreSQL;
- `proposal_policy='proposal_only'`;
- `human_approval_required=TRUE`;
- `auto_apply_enabled=FALSE`;
- máximo de cinco objetivos ativos por tenant;
- nenhuma rota de apply, merge, deploy ou migration.
