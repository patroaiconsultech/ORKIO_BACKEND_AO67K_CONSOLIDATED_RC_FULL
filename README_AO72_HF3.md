# AO72-HF3 — Missing direct_chat_persistence module

## Causa raiz
`main.py` importa `runtime/direct_chat_persistence.py`, mas o arquivo não existia no repositório. O Uvicorn falhava no boot com `ModuleNotFoundError`.

## Aplicação
Extraia este ZIP na raiz do backend. O arquivo será criado em:

`runtime/direct_chat_persistence.py`

Não substitua o `main.py`; o import atual já está correto.

## Testes
```bash
python -m py_compile runtime/direct_chat_persistence.py
python tests/ao72_hf3_direct_chat_persistence_smoke.py
```

## Rollback
Remover `runtime/direct_chat_persistence.py` não é recomendado enquanto o import permanecer em `main.py`.
O rollback correto é restaurar simultaneamente o `main.py` anterior que não possuía esse import.
