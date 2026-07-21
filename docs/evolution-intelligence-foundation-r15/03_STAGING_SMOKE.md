# Staging smoke plan

## 1. Ambiente

Configuração inicial segura:

```env
APP_ENV=staging

ALLOW_AUTOMATIC_MIGRATIONS=true
ALLOW_ALEMBIC_VERSION_NORMALIZATION=false

EVOLUTION_CENTER_ENABLED=true
EVOLUTION_KPI_COLLECTION_ENABLED=true
EVOLUTION_CONFIG_WRITE_ENABLED=false
EVOLUTION_HEALTH_SNAPSHOT_WRITE_ENABLED=false
EVOLUTION_PROPOSAL_GENERATION_ENABLED=false
EVOLUTION_PROPOSAL_ONLY=true
EVOLUTION_DIFF_PREVIEW_ENABLED=true
EVOLUTION_WRITE_ENABLED=false
EVOLUTION_AUTO_APPLY_ENABLED=false
EVOLUTION_HUMAN_APPROVAL_REQUIRED=true
EVOLUTION_ROLLBACK_REQUIRED=true
```

Se `alembic_version` precisar de normalização, habilitar
`ALLOW_ALEMBIC_VERSION_NORMALIZATION=true` somente para o primeiro boot
controlado e voltar para `false` após comprovação.

## 2. Boot

Confirmar:

```text
EVOLUTION_INTELLIGENCE_GOVERNANCE_OK
ORKIO_BOOT_IDENTITY
Application startup complete
```

Não pode existir:

```text
EVOLUTION_INTELLIGENCE_GOVERNANCE_FAILED
ORKIO_BOOT_IDENTITY_FAILED
```

## 3. Migration

Confirmar:

```text
alembic current = 0039_patch_evolution_intelligence_foundation
migration_in_sync=true
```

Verificar tabelas:

```text
evolution_objectives
evolution_kpi_targets
evolution_health_snapshots
```

## 4. Readonly

Como admin do tenant A:

```http
GET /api/admin/evolution/intelligence/runtime
GET /api/admin/evolution/intelligence/inventory
GET /api/admin/evolution/intelligence/health/preview
GET /api/admin/evolution/intelligence/diagnostics/preview
GET /api/admin/evolution/intelligence/priorities/preview
```

Critérios:

```text
write_executed=false
auto_apply_enabled=false
missing_dimensions inclui product enquanto não houver KPI real
sem dados nunca aparece como healthy
```

## 5. Cross-tenant

1. Criar objetivo no tenant A com config write temporariamente habilitado.
2. Tentar buscar o mesmo ID como tenant B.
3. Esperado: 404 ou 403.
4. Tentar vincular meta do tenant B ao objetivo A.
5. Esperado: bloqueio por serviço e constraint do banco.

## 6. Config write controlado

Habilitar temporariamente:

```env
EVOLUTION_CONFIG_WRITE_ENABLED=true
```

Criar no máximo cinco objetivos ativos. O sexto deve retornar:

```text
409 ACTIVE_OBJECTIVE_LIMIT_REACHED
```

Confirmar auditoria:

```http
GET /api/admin/evolution/intelligence/audit
```

Depois desabilitar novamente.

## 7. Health snapshot controlado

Habilitar temporariamente:

```env
EVOLUTION_HEALTH_SNAPSHOT_WRITE_ENABLED=true
```

Capturar com `approved=true`, confirmar hash/release identity e desabilitar.

## 8. Proposal-only

Habilitar temporariamente:

```env
EVOLUTION_PROPOSAL_GENERATION_ENABLED=true
```

Confirmar:

```text
mode=proposal_only
auto_apply=false
write_executed=false
diff_preview=null quando causa raiz não está confirmada
```

## 9. Estado estacionário

```env
ALLOW_AUTOMATIC_MIGRATIONS=false
ALLOW_ALEMBIC_VERSION_NORMALIZATION=false
EVOLUTION_CONFIG_WRITE_ENABLED=false
EVOLUTION_HEALTH_SNAPSHOT_WRITE_ENABLED=false
EVOLUTION_PROPOSAL_GENERATION_ENABLED=false
EVOLUTION_WRITE_ENABLED=false
EVOLUTION_AUTO_APPLY_ENABLED=false
```

Reiniciar staging e confirmar boot.
