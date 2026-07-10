# AO72-HF2 — Turn Lifecycle Premium Patch

## Objetivo
Corrigir a supressão indevida de respostas entre turnos diferentes e reduzir a corrida entre cancelamento SSE, conclusão do provider e persistência.

## Arquivos
- `main.py`
- `tests/ao72_hf2_turn_lifecycle_smoke.py`

## Alterações
- Idempotência do assistant passou a ser por turno:
  - `client_message_id` do usuário;
  - `trace_id` como fallback.
- A mensagem assistant persiste com uma chave derivada:
  - `assistant:<client_message_id|trace_id>`.
- O timeout/reconcile procura somente a resposta do turno atual.
- Uma desconexão do cliente não cancela mais à força a tarefa do provider; a tarefa pode concluir e persistir vinculada ao turno correto.

## Sem alteração
- Nenhuma migration.
- Nenhuma mudança no frontend.
- Nenhuma alteração no contrato SSE.
- Nenhuma mudança de wallet.

## Aplicação
Extraia o ZIP na raiz do repositório backend, substitua `main.py`, adicione o teste e faça deploy.

## Teste local
```bash
python -m py_compile main.py
python tests/ao72_hf2_turn_lifecycle_smoke.py
```

## Variáveis temporárias recomendadas durante validação
```env
ORKIO_EXECUTIVE_PREFLIGHT_ENABLED=0
AO70_QUALITY_ENGINE_ENABLED=1
AO70_QUALITY_RETRY_ENABLED=0
```

## Rollback
Restaurar o `main.py` anterior e redeployar.
