from runtime.intent_engine import build_intent_package, _infer_action_scope
from runtime.orion_capability_policy import (
    extract_mutation_constraints,
    is_explicit_ux_audit_request,
    is_readonly_technical_request,
)


ORION_CONTEXT = {
    "visible_agent": "orion",
    "target_agent_from_payload": "orion",
    "dest_mode": "single",
    "destination_contract_used": True,
}


def test_explicit_orion_technical_request_reaches_capability_runtime():
    payload = build_intent_package(
        "@Orion, gostaria que tu mapeasse o código da plataforma em modo read-only, sem proposta e sem escrita.",
        ORION_CONTEXT,
    )

    assert payload["intent"] == "platform_self_audit"
    assert payload["capability_name"] == "platform_self_audit"
    assert payload["action_scope"] == "diagnose"
    assert payload["requires_runtime_execution"] is True
    assert payload["target_agent"] == "orion"
    assert payload["target_agent_frozen"] == "orion"
    assert payload["ownership_locked"] is True
    assert payload["runtime_operation"]["explicit_destination_capability_routing"] is True
    assert payload["write_allowed"] is False
    assert payload["proposal_created"] is False
    assert payload["proposal_only"] is False
    assert payload["commit_executed"] is False
    assert payload["merge_executed"] is False
    assert payload["deploy_executed"] is False
    assert payload["migration_executed"] is False
    assert payload["human_approval_required"] is True


def test_explicit_orion_casual_message_remains_direct():
    payload = build_intent_package("Olá, Orion.", ORION_CONTEXT)

    assert payload["intent"] == "direct_agent_message"
    assert payload["capability_name"] == "direct_agent_message"
    assert payload["requires_runtime_execution"] is False
    assert payload["target_agent"] == "orion"


def test_negative_constraints_are_fail_closed_before_pr_substring():
    text = "Mapeie o código da plataforma em modo read-only, sem proposta e sem escrita."
    assert _infer_action_scope(text) == "diagnose"

    constraints = extract_mutation_constraints(text)
    assert constraints.explicit_readonly is True
    assert constraints.block_proposal is True
    assert constraints.block_write is True
    assert constraints.force_readonly is True


def test_do_not_open_pr_does_not_become_open_pr():
    text = "Audite o runtime, mas não abra PR e não faça deploy."
    assert _infer_action_scope(text) == "diagnose"


def test_apply_patch_without_deploy_remains_proposal_not_deploy():
    text = "Aplique o patch no código, mas não faça deploy."
    assert _infer_action_scope(text) == "propose_patch"


def test_orion_negative_constraints_remain_diagnose_and_fail_closed():
    payload = build_intent_package(
        "@Orion audite o runtime em modo read-only, sem proposta, sem escrita, nÃ£o abra PR, nÃ£o faÃ§a deploy.",
        ORION_CONTEXT,
    )

    assert payload["intent"] == "platform_self_audit"
    assert payload["action_scope"] == "diagnose"
    assert payload["target_agent"] == "orion"
    assert payload["target_agent_frozen"] == "orion"
    assert payload["ownership_locked"] is True
    assert payload["write_allowed"] is False
    assert payload["proposal_created"] is False
    assert payload["proposal_only"] is False
    assert payload["commit_executed"] is False
    assert payload["merge_executed"] is False
    assert payload["deploy_executed"] is False
    assert payload["migration_executed"] is False
    assert payload["human_approval_required"] is True


def test_readonly_technical_classifier_requires_action_and_scope():
    assert is_readonly_technical_request("Mapeie as rotas do backend em modo read-only")
    assert not is_readonly_technical_request("Olá, Orion")
    assert not is_readonly_technical_request("Aplique o patch no backend")


def test_ao17_requires_explicit_current_turn_ux_request():
    assert is_explicit_ux_audit_request(
        "Orion, audite a UX do onboarding e da interface mobile em modo read-only."
    )
    assert not is_explicit_ux_audit_request(
        "CEF-001A — Runtime, Route & Ownership Authority Map. "
        "O relatório histórico também menciona UX, onboarding, interface, mobile e PWA."
    )
    assert not is_explicit_ux_audit_request(
        "Não faça auditoria UX; prossiga com o Capability Registry."
    )
