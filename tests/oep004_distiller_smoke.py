from evolution.conversation import ConversationDistiller, distill_conversation
from evolution.conversation.models import DistillationResult

conversation = """
Daniel: Decidimos seguir com o OEP-004 em modo determinístico.
AO-01: Vamos criar o Conversation Distiller sem tocar chat, realtime ou voice.
Daniel: Houve erro anterior no KnowledgeEngine e isso gerou risco de regressão.
AO-01: A melhoria será manter contratos isolados e teste smoke.
Daniel: Aprendemos que não devemos avançar sem auditoria.
AO-01: Que tal registrar essa ideia no roadmap?
"""

result = ConversationDistiller().distill(conversation)

assert isinstance(result, DistillationResult)
assert result.proposal_only is True
assert result.write_executed is False
assert result.human_approval_required is True
assert result.metadata["llm_used"] is False
assert len(result.decisions) >= 1
assert len(result.actions) >= 1
assert len(result.bugs) >= 1
assert len(result.improvements) >= 1
assert len(result.ideas) >= 1
assert len(result.lessons) >= 1
assert len(result.risks) >= 1
assert result.confidence > 0

result2 = distill_conversation("Vamos testar o distiller.")
assert len(result2.actions) >= 1

print("OEP004_CONVERSATION_DISTILLER_SMOKE_PASS")
