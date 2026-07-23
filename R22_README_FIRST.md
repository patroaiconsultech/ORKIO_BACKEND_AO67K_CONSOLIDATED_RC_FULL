# ORKIO Backend R22 — Patch Only / Root Ready

## Aplicação

Extraia o ZIP e envie **o conteúdo interno** para a raiz do repositório backend,
preservando os caminhos:

- `runtime/agent_turn_context.py`
- `schemas/document_artifacts.py`
- `tests/test_explicit_agent_ownership_r22.py`
- `tests/test_document_artifact_schema_r22.py`

Não crie uma pasta `ORKIO_BACKEND_R22_PATCH_ONLY_ROOT_READY` dentro do repositório.

## O que este pacote altera

1. Ownership explícito e imutável para `orkio`, `orion`, `chris` e `laura`.
2. Reconhecimento de Laura nos contratos de ownership e SSE.
3. Correção do crash DOCIO causado por `source_plan` no payload interno.
4. Preservação de `source_plan` apenas em subclasses internas que declarem o campo.
5. Testes de regressão.

## O que este pacote NÃO altera

- `main.py`
- `__init__.py`
- `runtime/__init__.py`
- Dockerfile
- Railway start command
- banco ou migrations
- frontend
- Team runtime

Team permanece propositalmente sem ownership bloqueado até haver integração
e teste end-to-end do caminho SSE, persistência e evento terminal.

## Validação antes do deploy

```bash
python -m py_compile runtime/agent_turn_context.py schemas/document_artifacts.py
python -m pytest -q   tests/test_explicit_agent_ownership_r22.py   tests/test_document_artifact_schema_r22.py
PYTHONPATH=/ python -c "import app.main; print('ORKIO_MAIN_IMPORT_OK')"
```

## Smoke após deploy

1. Selecionar Orkio, Orion, Chris e Laura individualmente.
2. Confirmar a mesma autoria no payload SSE, persistência e frontend.
3. Gerar PPTX pelo DOCIO e confirmar ausência de:
   `source_plan Extra inputs are not permitted`.
4. Confirmar que o stream termina em `done`, ou `error` seguido de `done`.
5. Não habilitar `TEAM_REAL_AGENT_EXECUTION_V1`.

## Rollback

Reverter o commit que introduziu estes quatro arquivos, ou restaurar as versões
anteriores de:

- `runtime/agent_turn_context.py`
- `schemas/document_artifacts.py`

Não há migration.
