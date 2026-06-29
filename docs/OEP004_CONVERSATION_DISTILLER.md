# OEP-004 — Conversation Distiller

Módulo backend-only, determinístico e desacoplado para transformar conversas em conhecimento estruturado.

Não toca chat, realtime, voice, frontend, banco ou LLM.

## Teste

```bash
PYTHONPATH=. python -m py_compile evolution/*.py evolution/conversation/*.py tests/oep004_distiller_smoke.py
PYTHONPATH=. python tests/oep004_distiller_smoke.py
```

Esperado:

```txt
OEP004_CONVERSATION_DISTILLER_SMOKE_PASS
```
