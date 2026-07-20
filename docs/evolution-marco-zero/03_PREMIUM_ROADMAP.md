# Caminho até o premium

## Fase R1 — Preview seguro

Estado deste pacote:

```text
tenant_bound=true
database_only=true
write_enabled=false
migration=false
rollback_data_required=false
```

Objetivo: obter um inventário readonly confiável.

## Fase R1.1 — Tenant hardening do Evolution Admin

Antes de habilitar qualquer mutação, revisar e vincular ao tenant canônico:

```text
GET  /api/admin/evolution/proposals
GET  /api/admin/evolution/proposals/{proposal_id}
POST /api/admin/evolution/proposals/{proposal_id}/approve
POST /api/admin/evolution/proposals/{proposal_id}/reject
GET  /api/admin/evolution/executions
```

Critério: nenhum ID global pode atravessar tenant.

## Fase R2 — Baseline persistente e aplicação governada

Migration proposta: `0038_evolution_marco_zero_baselines`.

Tabelas propostas:

```text
evolution_baselines
evolution_baseline_items
```

Campos mínimos do baseline:

```text
baseline_id
org_slug
status
cutoff_at
candidate_count
candidate_digest
idempotency_key
reason
approved_by
previewed_at
applied_at
rolled_back_at
created_at
```

Campos mínimos dos itens:

```text
baseline_id
proposal_id
previous_status
previous_updated_at
archived_at
archived_by
rollback_status
```

A aplicação exige:

```text
EVOLUTION_MARCO_ZERO_WRITE_ENABLED=true
approved=true
reason obrigatório
preview digest válido
candidate_count inalterado
idempotency key
transação única
audit log
```

## Fase R2.1 — Rollback governado

```text
preview rollback
aprovação humana
restauração somente dos itens do baseline
audit log
idempotência
cross-tenant delta=0
```

## Fase R3 — KPIs evidence-based

Cada métrica deve declarar:

```text
metric_id
classification
score
sample_count
confidence
measured_at
window_start
window_end
baseline_id
sources
missing_sources
formula_version
included_in_overall
```

Classificações:

```text
measured
estimated
configuration_detected
insufficient_evidence
unavailable
```

## Fase R4 — Conhecimento medido por agente

Usar avaliações reais:

```text
agent_id
capability_id
score
sample_count
confidence
evidence_ref
evaluator_ref
evaluation_version
created_at
```

Configuração detectada nunca vira score de competência.

## Fase R5 — Observabilidade e histórico premium

```text
snapshots 7/30/90 dias
deployment commit
request ID
baseline correlation
latência
sucesso/falha
eventos terminais
tenant isolation proof
```

## Fase R6 — Autoevolução assistida

Mesmo no estado premium:

```text
proposal_only=true
human_approval_required=true
commit_executed=false por padrão
merge_executed=false por padrão
deploy_executed=false por padrão
```

KPIs podem orientar propostas. Não podem autorizar mutação autônoma.
