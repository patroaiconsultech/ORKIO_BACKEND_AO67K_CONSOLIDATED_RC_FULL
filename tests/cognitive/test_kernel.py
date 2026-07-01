from app.cognitive.contracts import CognitiveRequest
from app.cognitive.event_bus import InMemoryEventBus
from app.cognitive.kernel import CognitiveMicrokernel
from app.cognitive.plugins.core import register_core_plugins
from app.cognitive.registry import PluginRegistry


def make_kernel():
    registry = register_core_plugins(PluginRegistry())
    bus = InMemoryEventBus()
    return CognitiveMicrokernel(registry=registry, event_bus=bus, mode="shadow"), bus


def test_kernel_builds_decision_envelope_for_technical_request():
    kernel, bus = make_kernel()
    request = CognitiveRequest(
        user_id="daniel",
        tenant_id="patroai",
        message="Precisamos auditar bug de deploy no backend.",
        metadata={"is_superadmin": True},
    )

    envelope = kernel.handle(request)

    assert envelope.intent == "technical_audit_or_patch"
    assert envelope.runtime == "agent.dev"
    assert envelope.executor == "DevAgent"
    assert envelope.policy_status == "approved_shadow_superadmin"
    assert envelope.proposal_only is True
    assert len(envelope.plan) >= 4
    assert any(event.name == "DecisionEnvelopeBuilt" for event in bus.events())


def test_kernel_marks_deploy_as_critical_risk():
    kernel, _ = make_kernel()
    request = CognitiveRequest(
        user_id="operator",
        tenant_id="patroai",
        message="Faça deploy em produção agora.",
    )

    envelope = kernel.handle(request)

    assert envelope.risk_level == "critical"
    assert envelope.plan[-1]["action"] == "require_human_approval"
