# EPIC-002D-R1 — APP CORE IMPORT HYGIENE TARGET LOCKED

## Objetivo

Desbloquear o próximo erro integrado observado:

```text
ModuleNotFoundError: No module named 'app.core'
```

Cadeia:

```text
runtime.intent_engine
→ services.governance_service
→ app.core.orkio_constitution
```

## Decisão

Este EPIC é target-only. Ele altera somente:

```text
services/governance_service.py
```

## Regra

Substituir imports legados:

```python
from app.core.orkio_constitution import ...
```

por:

```python
from core.orkio_constitution import ...
```

## Justificativa

O baseline atual já usa namespaces de raiz em outros pontos (`services.*`, `runtime.*`, `config.*`).
Criar `app.core` como shim aumentaria entropia e criaria autoridade paralela de namespace.

## Risco

Baixo, desde que validado em branch/shadow.

## Rollback

```bash
git checkout -- services/governance_service.py
```

## Critérios de aceite

- aplicador idempotente;
- auditoria target-only passa;
- somente `services/governance_service.py` modificado;
- nenhum shim criado;
- nenhum fallback `{}` criado;
- novo erro integrado, se existir, deve ser tratado em EPIC separado.
