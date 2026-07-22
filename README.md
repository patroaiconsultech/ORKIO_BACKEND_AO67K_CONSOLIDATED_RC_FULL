# ORKIO Premium 3.0 Foundation

Pacote inicial em `proposal_only` para introduzir:

- Architecture Contract
- Attachment Resolution Contract
- Execution Profile Contract
- Decision Receipts
- Agent Safety Boundary
- Shadow Mode

## Estado padrão

```text
shadow_mode=true
enforcement=false
proposal_only=true
execution_allowed=false
default_deny=true
```

## Integração segura

Não substituir `app/main.py`.

Importar somente o bootstrap do OCIL no ponto em que a mensagem já foi recebida e antes da seleção definitiva de contexto/runtime.

Exemplo conceitual:

```python
from app.services.ocil.foundation import build_shadow_decision

decision = build_shadow_decision(
    message_id=message_id,
    thread_id=thread_id,
    requested_agent=requested_agent,
    current_attachment_ids=current_attachment_ids,
    historical_attachment_ids=historical_attachment_ids,
    explicit_historical_context_requested=explicit_historical_context_requested,
    user_intent=user_message,
)

logger.info("OCIL_SHADOW_DECISION %s", decision.to_json())
```

O retorno do OCIL não deve alterar o pipeline atual enquanto:

```text
OCIL_ATTACHMENT_ENFORCEMENT_ENABLED=false
OCIL_EXECUTION_ENFORCEMENT_ENABLED=false
```

## Promoção para enforcement

Promover somente quando:

1. o anexo correto for resolvido em todos os cenários de validação;
2. divergências forem explicáveis;
3. nenhum agente receber capacidades implícitas;
4. receipts forem persistidos ou exportados de modo auditável;
5. rollback por feature flag estiver testado.

## Observação

Este pacote não conhece o ORM, o modelo de mensagem nem o registry real do repositório ORKIO. Os adapters de banco e runtime devem ser conectados no projeto real sem mover a lógica para `app/main.py`.
