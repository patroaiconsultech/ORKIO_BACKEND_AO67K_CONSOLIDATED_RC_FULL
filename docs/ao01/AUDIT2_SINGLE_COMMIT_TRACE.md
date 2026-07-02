# AO-01 AUDIT2 — Single Commit Trace

## Objetivo

Isolar a causa da duplicação de respostas no `/api/chat/stream` após o EOS-06/AO85 assumir corretamente o turno.

## Estado comprovado

- O backend está de pé.
- O stream retorna `200 OK`.
- O EOS-06/AO85 já assume turnos executivos.
- O `guard_force=True` aparece em runtime.
- O payload EOS-06 aparece como `handled=True`.
- Os fast-paths legados foram bloqueados.
- O problema restante é duplicação de resposta em alguns turnos, principalmente governança/proposal_only.

## Hipótese primária

A duplicação não nasce mais no roteamento. Ela nasce em uma das camadas abaixo:

1. persistência do assistant no backend;
2. reconciliação do frontend após `done`;
3. reload de `/api/messages`;
4. registro de execução/flow gerando segunda mensagem;
5. mismatch entre mensagem temporária do stream e mensagem persistida.

## Marcadores obrigatórios

Adicionar logs temporários com estes nomes exatos:

```text
AUDIT2_SINGLE_COMMIT_TRACE stream_start
AUDIT2_SINGLE_COMMIT_TRACE eos06_payload_built
AUDIT2_SINGLE_COMMIT_TRACE assistant_persist_attempt
AUDIT2_SINGLE_COMMIT_TRACE assistant_persist_result
AUDIT2_SINGLE_COMMIT_TRACE sse_chunk_emit
AUDIT2_SINGLE_COMMIT_TRACE sse_done_emit
AUDIT2_SINGLE_COMMIT_TRACE stream_return
AUDIT2_SINGLE_COMMIT_TRACE messages_reload
AUDIT2_SINGLE_COMMIT_TRACE frontend_reconcile
```

## Campos mínimos em cada log

```text
trace_id
thread_id
assistant_message_id
client_temp_id
persist_source
route_family
category
already_persisted
message_hash
answer_len
created_at
```

## Onde instrumentar no backend

### 1. Antes de chamar `eos06_build_router_precedence_payload`

Registrar:

```text
stream_start
```

### 2. Logo após `eos06_build_router_precedence_payload(message)`

Registrar:

```text
eos06_payload_built
```

Campos:

```text
handled
category
route_family
answer_len
```

### 3. Antes de `_persist_assistant_message`

Registrar:

```text
assistant_persist_attempt
```

Campos:

```text
persist_source=eos06_hf2_turn_ownership
message_hash
answer_len
```

### 4. Depois de `_persist_assistant_message`

Registrar:

```text
assistant_persist_result
```

Campos:

```text
assistant_message_id
assistant_persisted
already_persisted
```

### 5. Antes do `yield _metatron_sse("chunk", ...)`

Registrar:

```text
sse_chunk_emit
```

### 6. Antes do `yield _metatron_sse("done", ...)`

Registrar:

```text
sse_done_emit
```

Campos obrigatórios no payload de `done`:

```text
assistant_persisted
assistant_message_id
trace_id
thread_id
route_family
message_hash
```

### 7. Imediatamente antes do `return` do bloco EOS-06

Registrar:

```text
stream_return
```

## Onde instrumentar no frontend

### 1. Antes de criar mensagem temporária do assistant

Registrar no console:

```text
AUDIT2_SINGLE_COMMIT_TRACE frontend_temp_assistant_create
```

Campos:

```text
trace_id
thread_id
client_temp_id
```

### 2. Ao receber evento `done`

Registrar:

```text
AUDIT2_SINGLE_COMMIT_TRACE frontend_done_received
```

Campos:

```text
trace_id
thread_id
assistant_message_id
client_temp_id
```

### 3. Ao reconciliar mensagem temporária com persistida

Registrar:

```text
AUDIT2_SINGLE_COMMIT_TRACE frontend_reconcile
```

Campos:

```text
trace_id
thread_id
assistant_message_id
client_temp_id
matched
```

### 4. Ao recarregar `/api/messages`

Registrar:

```text
AUDIT2_SINGLE_COMMIT_TRACE messages_reload
```

Campos:

```text
thread_id
message_count
assistant_ids
```

## Critério de diagnóstico

### Caso A — backend persiste duas vezes

Haverá dois `assistant_persist_result` para o mesmo `trace_id` e `message_hash`.

### Caso B — backend persiste uma vez, frontend mostra duas

Haverá um único `assistant_persist_result`, mas a UI terá:

```text
frontend_temp_assistant_create
frontend_done_received
messages_reload
```

sem `frontend_reconcile matched=true`.

### Caso C — execução governada gera segunda resposta

Haverá um `assistant_persist_result` EOS-06 e depois outro evento com `persist_source` diferente, possivelmente ligado a execution/flow/reconcile.

## Correção provável depois da auditoria

Se for frontend:

```text
Ao receber done com assistant_message_id:
  substituir mensagem temporária pelo ID persistido
  não adicionar nova bolha se o texto/hash já existir no turno
```

Se for backend:

```text
Antes de persistir:
  buscar mensagem assistant do mesmo trace_id/thread_id/message_hash
  se existir, reutilizar ID e não inserir de novo
```

## Veredito AO-01

Este AUDIT2 não altera comportamento. Ele só torna observável quem criou a segunda resposta.
