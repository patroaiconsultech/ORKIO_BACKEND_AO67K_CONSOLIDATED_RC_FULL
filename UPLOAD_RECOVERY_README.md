# ORKIO backend recovery upload

## Objetivo

Corrigir o crash de boot:

```text
ModuleNotFoundError: No module named 'app.runtime.document_artifact_intent'
```

## Diagnostico

O `main.py` importado no Railway registra SEC-001 e DOCIO, mas o deploy nao contem toda a cadeia de arquivos importada por esse `main.py`.

Este pacote deve ser aplicado no root do backend, no mesmo nivel de:

```text
main.py
__init__.py
runtime/
routes/
schemas/
services/
```

Nao subir este ZIP como uma pasta nova dentro do repositorio. Os caminhos internos ja estao prontos para upload direto.

## Arquivos incluidos

```text
main.py
__init__.py
routes/__init__.py
routes/access_grants.py
routes/document_artifacts.py
runtime/__init__.py
runtime/capability_registry.py
runtime/document_artifact_intent.py
schemas/access_grants.py
schemas/document_artifacts.py
services/access_grant_service.py
services/document_artifact_command_service.py
services/document_artifact_service.py
services/document_context_service.py
services/document_governance_service.py
```

## Validacao local

```text
py_compile=PASS
boot_crash_targeted=true
merge_executed=false
deploy_executed=false
database_write_executed=false
```

## Comando normal do Railway

Depois do upload e deploy, o start command esperado para backend continua:

```text
python -m uvicorn --app-dir / --log-config /app/logging_uvicorn_stdout.json app.main:app --host 0.0.0.0 --port ${PORT:-8080} --timeout-keep-alive 75
```

