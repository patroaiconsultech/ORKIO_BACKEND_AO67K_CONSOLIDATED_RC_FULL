# ORKIO Executive Cognitive System RC-1

## Objetivo

Elevar o Orkio de agente conversacional para copiloto executivo cognitivo, com identidade,
raciocínio, governança, catálogo de capacidades e disciplina de verdade operacional.

## Escopo

Este RC-1 adiciona fundação modular sem alterar runtime crítico.

Inclui:

- `agents/orkio/identity.py`
- `agents/orkio/reasoning.py`
- `agents/orkio/decision_engine.py`
- `agents/orkio/capability_resolver.py`
- `agents/orkio/truth_engine.py`
- `agents/orkio/orchestration.py`
- `agents/orkio/communication.py`
- `runtime/orkio_cognitive_system.py`
- `knowledge/platform/*.yaml`

## Não altera

- Banco de dados
- Deploy
- SSE
- Frontend
- Auth
- Realtime
- Provedores LLM

## Governança

Toda evolução estrutural deve manter:

- `observe_only=true`
- `proposal_only=true`
- aprovação humana obrigatória
- diff preview
- risco
- rollback
- validação

## Integração futura

O `main.py` poderá importar:

```python
from runtime.orkio_cognitive_system import build_orkio_executive_answer
```

e consultar o retorno antes de fast-paths públicos quando a intenção for
`platform_capability`.

## Smoke local

```bash
python - <<'PY'
from runtime.orkio_cognitive_system import executive_system_smoke
print(executive_system_smoke())
PY
```

Esperado:

```text
ORKIO_EXECUTIVE_COGNITIVE_SYSTEM_RC1_OK
```
