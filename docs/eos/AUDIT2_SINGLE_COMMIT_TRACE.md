# AUDIT2 — Single Commit Trace

## Objetivo

Identificar se a duplicação de resposta vem de segundo emissor, segundo persistidor ou reconciliação de thread.

## Pontos a instrumentar

- STREAM_START
- STREAM_FIRST_CHUNK
- ASSISTANT_MESSAGE_CREATE
- ASSISTANT_MESSAGE_PERSIST
- THREAD_APPEND
- STREAM_DONE
- RECONCILE_START
- RECONCILE_END

## Campos obrigatórios de log

```text
trace_id
thread_id
assistant_message_id
persist_source
already_exists
stack_origin
```

## Critério de diagnóstico

Se o mesmo `trace_id` gerar dois `ASSISTANT_MESSAGE_PERSIST`, a causa é persistência duplicada.

Se houver um único persist no backend e duas bolhas no frontend, a causa é reconciliação/renderização no frontend.

## Regra de segurança

Este AUDIT2 não deve alterar comportamento. Apenas logs.
