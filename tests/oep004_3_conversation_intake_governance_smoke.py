from evolution.conversation.distiller import ConversationDistiller
from evolution.conversation.governed_distiller import GovernedConversationDistiller
from evolution.conversation.intake import ConversationIntake
from evolution.conversation.privacy import PrivacyScanner


text = """
Daniel informou: vamos corrigir o contrato do módulo.
Também houve erro no repository.
Contato de teste: pessoa@example.com.
"""

intake = ConversationIntake(
    conversation_text=text,
    tenant_id="tenant_orkio",
    user_id="user_daniel",
    thread_id="thread_oep004",
    conversation_id="conv_oep004_3",
    consent_granted=True,
    retention_policy="standard",
    source="smoke",
)

payload = intake.to_payload()
assert payload["tenant_id"] == "tenant_orkio"
assert payload["thread_id"] == "thread_oep004"
assert payload["content_hash"]
assert payload["idempotency_key"]
assert payload["proposal_only"] is True
assert payload["write_executed"] is False
assert payload["human_approval_required"] is True

same = ConversationIntake(
    conversation_text=" ".join(text.split()),
    tenant_id="tenant_orkio",
    user_id="user_daniel",
    thread_id="thread_oep004",
    consent_granted=True,
)
assert same.idempotency_key == intake.idempotency_key

try:
    ConversationIntake(
        conversation_text=text,
        tenant_id="tenant_orkio",
        user_id="user_daniel",
        thread_id="thread_oep004",
        consent_granted=False,
    ).to_payload()
    raise AssertionError("expected consent failure")
except PermissionError:
    pass

scan = PrivacyScanner().scan(text)
assert scan.has_pii is True
assert "email" in scan.pii_types
assert "[REDACTED_EMAIL]" in scan.redacted_text

governed = GovernedConversationDistiller(ConversationDistiller())
result = governed.distill_intake(intake)

assert result["privacy"]["has_pii"] is True
assert result["proposal_only"] is True
assert result["write_executed"] is False
assert result["human_approval_required"] is True
assert result["distillation"]

print("OEP004_3_CONVERSATION_INTAKE_GOVERNANCE_PASS")
