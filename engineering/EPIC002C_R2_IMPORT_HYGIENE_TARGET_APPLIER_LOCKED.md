# EPIC-002C-R2 — Import Hygiene Target Applier Locked

## Objetivo

Resolver apenas a quebra inicial de import em `runtime/intent_engine.py`,
sem expandir escopo para todo o repositório.

## Evidência de motivação

O EPIC-002B não consegue ser validado integrado porque importar:

```python
runtime.orkio_runtime_foundation.persistence
```

executa a cadeia de import de `runtime/__init__.py`, que alcança `runtime/intent_engine.py`.

O arquivo usa imports legados:

```python
app.config.runtime
app.services.governance_service
app.runtime.capability_registry
```

Mas o baseline real usa caminhos raiz:

```python
config.runtime
services.governance_service
runtime.capability_registry
```

## Decisão R2

Remover o patch textual e usar aplicador Python target-only como mecanismo oficial.

## Fora de escopo

O próximo erro conhecido:

```text
ModuleNotFoundError: No module named 'app.core'
```

deve ser tratado em EPIC separado.
