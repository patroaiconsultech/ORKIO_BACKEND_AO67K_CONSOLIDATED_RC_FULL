# Contrato MZ-001-R1

## Endpoint

```text
POST /api/admin/evolution/archive-baseline
POST /api/admin/evolution/proposals/archive-baseline
```

## Requisitos

```text
admin autenticado
tenant da sessão
X-Org-Slug ausente ou igual ao tenant da sessão
EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED=true
dry_run=true
PostgreSQL disponível
```

## Resposta

```json
{
  "ok": true,
  "version": "MZ-001-R1",
  "mode": "governed_marco_zero_preview_only",
  "dry_run": true,
  "preview_only": true,
  "write_enabled": false,
  "write_executed": false,
  "database_write_executed": false,
  "delete_executed": false,
  "human_approval_required": true,
  "schema_bootstrap_executed": false,
  "memory_fallback_used": false,
  "source": "postgresql",
  "candidate_count": 0,
  "already_archived_count": 0,
  "proposal_ids_preview": [],
  "preview_limit": 50,
  "preview_truncated": false,
  "cutoff_at": 0,
  "generated_at": 0
}
```

## Fail-closed

```text
preview flag false → 403 EVOLUTION_MARCO_ZERO_PREVIEW_DISABLED
dry_run=false → 403 EVOLUTION_MARCO_ZERO_WRITE_DISABLED
tenant divergente → 403 Tenant mismatch
PostgreSQL indisponível → 503
cutoff inválido → 422
```

O parâmetro legado `confirm` é aceito apenas para compatibilidade. Ele não
autoriza escrita e não é tratado como segredo.
