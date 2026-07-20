# ORKIO MZ-001-R1 — Backend preview-only

## Baseline

```text
artifact_source=ORKIO_BACKEND_AO67K_CONSOLIDATED_RC_FULL-main (42).zip
artifact_sha256=a1b1534683aaa200482a96d43fc8d912a693bf0414239999ed03d0cef42faf7a
main_before_sha256=c54a9e34facab8cab88fced9dd5caabbadcef4edbfd9bc9a13ca3383fd690d81
main_after_sha256=44691d8b7383600cc0df6fce4000e23b46cdd82aa1d3e3de00c0ebe4931d4f09
```

Este pacote foi construído diretamente sobre o backend de produção `(42)`.

## Objetivo

Transformar `POST /api/admin/evolution/archive-baseline` em uma operação
estritamente readonly:

- tenant derivado da identidade canônica;
- header divergente falha com 403;
- PostgreSQL obrigatório;
- sem fallback em memória;
- contagem exata;
- preview limitado a 50 IDs;
- nenhuma escrita;
- nenhuma migration;
- nenhuma aplicação real.

## Estado padrão

```text
EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED=false
write_enabled=false
write_executed=false
database_write_executed=false
human_approval_required=true
```

O endpoint só produz preview depois que a flag de preview for explicitamente
habilitada no ambiente.
