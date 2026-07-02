# Runtime Foundation

## Objetivo

Uma mensagem do usuário deve gerar:

1. uma classificação;
2. uma resposta;
3. uma persistência assistant;
4. um evento `done`;
5. uma liberação de input.

## Eventos mínimos

- STREAM_REQUEST_ENTER
- STREAM_FIRST_STATUS
- KERNEL_DECISION_READY
- ASSISTANT_PERSIST_ATTEMPT
- ASSISTANT_PERSIST_CREATED ou ASSISTANT_PERSIST_SKIPPED_DUPLICATE
- STREAM_DONE_EMITTED
- TERMINAL_GUARD_V7_UNLOCK

## Critério de aceite

Nenhum `trace_id` pode persistir duas mensagens assistant equivalentes.
