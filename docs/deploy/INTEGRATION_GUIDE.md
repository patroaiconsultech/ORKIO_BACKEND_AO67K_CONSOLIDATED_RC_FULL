# Integration Guide

## Integração futura no `/api/chat/stream`

Este pacote é aditivo. Para integrar no runtime real, inserir o hook no ponto onde hoje o stream já possui:

- `trace_id`
- `thread_id`
- `user_message`
- contexto do agente
- contexto de usuário

## Pseudocódigo seguro

```python
from runtime.orkio_kernel import build_orkio_kernel_response
from runtime.orkio_runtime_foundation import TerminalGuardV7Trace, PersistenceIdempotencyGuard

guard = TerminalGuardV7Trace(trace_id=trace_id, thread_id=thread_id)
guard.open()

kernel_result = build_orkio_kernel_response(
    message=user_message,
    user_context=user_context,
    thread_context=thread_context,
    capability_registry=capability_registry,
)

guard.kernel_ready(category=kernel_result.classification.category)

persist_guard = PersistenceIdempotencyGuard()
persist_key = persist_guard.build_key(trace_id, thread_id, kernel_result.assistant_turn_id)

if persist_guard.should_persist(persist_key):
    # call existing persistence function once
    persist_guard.mark_persisted(persist_key)

yield status
yield chunk/final_text
guard.done()
yield done
guard.unlock()
return
```

## Regra

Não deixar o fluxo continuar para persistidores legados após `kernel_result.handled=True`.
