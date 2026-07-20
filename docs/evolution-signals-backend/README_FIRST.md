# ORKIO Evolution Signals V1 — Production 41 Surgical Patch

## Baseline comprovada

```text
artifact_source=ORKIO_BACKEND_AO67K_CONSOLIDATED_RC_FULL-main (41).zip
artifact_sha256=855b0fe8c0b862f02727bd1a9c909195ea47c92b5f9f5c91d2ff6b1f45957ba6
artifact_entries=1050
artifact_integrity=PASS

main_before_sha256=35daf4bef0765b197f3c6def1633fd890da476fe5c0fe237a65537dd92485ea5
main_after_sha256=d9eb8b8c11f5b673808d6f01c3df48252e64b5f612b4675770c9fd7d6253177d
main_lines_before=53192
main_lines_after=53208
main_added_lines=16
main_removed_lines=0
```

Este pacote foi reconstruído diretamente sobre a produção `(41)`.

O `main.py` incluído é o arquivo completo da produção `(41)` com somente:

1. import do router Evolution Signals;
2. registro do router Evolution Signals.

Nenhuma linha da produção `(41)` foi removida.

## Rotas novas

```text
GET  /api/admin/evolution/signals/current
GET  /api/admin/evolution/signals/history
POST /api/admin/evolution/signals/snapshots/capture
POST /api/admin/evolution/agent-evaluations
```

## Estado seguro inicial

```text
EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED=false
EVOLUTION_AGENT_EVAL_WRITE_ENABLED=false
ACCESS_GATE_REQUIRE_FOR_AUTH=false
```

Os GETs são readonly. Os POSTs permanecem bloqueados.
