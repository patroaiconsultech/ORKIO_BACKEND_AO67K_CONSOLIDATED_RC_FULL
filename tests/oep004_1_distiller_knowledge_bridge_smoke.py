from evolution.conversation.distiller import ConversationDistiller
from evolution.conversation.knowledge_bridge import result_to_knowledge_documents


conversation = """
Decidimos preservar o Knowledge Vault como base.
Vamos corrigir o contrato do repositório.
Existe risco de acoplamento indevido com o chat.
Aprendemos que smoke tests precisam rodar antes do patch.
"""

distiller = ConversationDistiller()
result = distiller.distill(conversation)
documents = result_to_knowledge_documents(result)

assert len(documents) >= 2

for doc in documents:
    assert doc["proposal_only"] is True
    assert doc["write_executed"] is False
    assert doc["human_approval_required"] is True
    assert doc["source"] == "conversation_distiller"

assert any("summary" in doc["tags"] for doc in documents)
assert any("risk" in doc["tags"] for doc in documents)

print("OEP004_1_DISTILLER_KNOWLEDGE_BRIDGE_PASS")
