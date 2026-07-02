import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "runtime" / "executive_intelligence.py"
SPEC = importlib.util.spec_from_file_location("executive_intelligence", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


envelope = MODULE.build_executive_context_envelope(
    intent_package={
        "intent": "business_advisory",
        "objective": "increase margin with controlled risk",
        "runtime_operation": {"requires_capability": "financial_model_review"},
    },
    eos_health={
        "status": "ok",
        "checks": {"bootstrap": "ok", "eos_health": "ok"},
    },
    capability_registry={
        "orkio": {
            "capabilities": ["financial_model_review", "product_roadmap_review"],
            "governed": True,
        }
    },
)

assert envelope["mode"] == "observe_only"
assert envelope["governance_context"]["proposal_only"] is True
assert envelope["governance_context"]["write_executed"] is False
assert envelope["governance_context"]["human_approval_required"] is True
assert envelope["operational_context"]["health"]["evidence_level"] == "declared_foundation"
assert envelope["operational_context"]["health"]["operational_state_proven"] is False
assert envelope["operational_context"]["capabilities"]["availability_proven"] is False

live = MODULE.build_executive_context_envelope(
    eos_health={
        "status": "ok",
        "checks": {
            "database": "ok",
            "provider": "ok",
            "queue": "ok",
            "realtime": "ok",
            "agents": "ok",
            "storage": "ok",
        },
    },
    capability_registry={},
)
assert live["operational_context"]["health"]["evidence_level"] == "live_operational"
assert live["operational_context"]["health"]["operational_state_proven"] is True

overlay = MODULE.build_executive_intelligence_overlay(envelope)
assert MODULE.EOS06_VERSION in overlay
assert "proposal_only=true" in overlay
assert "write_executed=false" in overlay
assert "human_approval_required=true" in overlay

base_prompt = "Base executive prompt"
combined = MODULE.append_executive_intelligence(base_prompt, envelope)
assert combined.startswith(base_prompt)
assert combined.count(MODULE.EOS06_VERSION) == 1
assert MODULE.append_executive_intelligence(combined, envelope) == combined

print("EOS06_EXECUTIVE_INTELLIGENCE_PASS")
