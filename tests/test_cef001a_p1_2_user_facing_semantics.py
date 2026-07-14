from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
app_alias = types.ModuleType("app")
app_alias.__path__ = [str(ROOT / "app"), str(ROOT)]  # type: ignore[attr-defined]
sys.modules.setdefault("app", app_alias)

from routes.internal.orion_internal import (
    OrionRuntimeIn,
    _build_platform_self_audit_payload,
    _build_single_target_specialist_dispatch_payload,
    platform_self_evolution_plan,
)
from runtime.execution_evidence_contract import apply_execution_evidence_to_envelope


BANNED_TRACE_LITE_FRAGMENTS = (
    "EXECUTED",
    "executou",
    "executada",
    "executado",
    "dispatch real",
    "execução confirmada",
    "execucao confirmada",
    "dispatch confirmado",
)


USER_FACING_KEYS = (
    "technical_summary",
    "executive_diagnostic",
    "backend_assessment",
    "frontend_assessment",
    "integration_assessment",
    "confirmed_evidence",
    "main_risk",
    "recommended_actions",
    "final_consolidation",
    "architecture_notes",
    "remediation_plan",
    "source_audit_event",
)


def _text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _assert_trace_lite_payload(payload: dict[str, Any]) -> None:
    assert payload["dispatch_executed"] is False
    assert payload["execution_claim"] == "not_verified"
    assert payload["verification_level"] == "trace_lite"
    assert payload["execution_depth"] == "trace_lite"
    assert payload["auditability_status"] == "trace_lite_not_verified"
    assert not str(payload.get("event") or "").endswith("_EXECUTED")

    user_facing = {key: payload.get(key) for key in USER_FACING_KEYS if key in payload}
    rendered = _text(user_facing)
    lowered = rendered.lower()
    for fragment in BANNED_TRACE_LITE_FRAGMENTS:
        assert fragment.lower() not in lowered


def test_platform_self_audit_trace_lite_user_facing_semantics_are_canonical():
    inp = OrionRuntimeIn(message="@Orion audite o runtime em modo read-only", include_frontend=False)
    payload = _build_platform_self_audit_payload(inp, "orion")

    _assert_trace_lite_payload(payload)
    assert payload["status"] == "ready"


def test_single_target_template_trace_lite_metadata_and_content_are_coherent():
    payload = _build_single_target_specialist_dispatch_payload(
        message="@Orion peça ao backend_engineer status ok",
        target_agent="backend_engineer",
        delegated_by="orion",
    )

    _assert_trace_lite_payload(payload)
    assert payload["status"] == "simulated"
    assert payload["visible_agent"] == "orion"
    assert payload["final_speaker"] == "orion"
    assert payload["simulated_final_speaker"] == "backend_engineer"
    assert payload["authorship_status"] == "simulated_template_not_invoked"
    assert payload["specialist_invoked"] is False
    assert payload["specialist_response_verified"] is False
    assert payload["authorship_claim"] == "not_verified"
    assert "backend operational" not in payload["message"].lower()
    assert "nao deve ser atribuida" in payload["message"].lower()
    assert payload["planned_specialist_answer"]
    assert payload["specialist_invocation_verified"] is False
    assert payload["specialist_reports"][0]["report_status"] == "simulated"
    assert payload["specialist_reports"][0]["evidence_verified"] is False
    assert payload["specialist_reports"][0]["specialist_invoked"] is False
    assert payload["specialist_reports"][0]["specialist_response_verified"] is False
    assert payload["specialist_reports"][0]["authorship_claim"] == "not_verified"
    assert "planned_specialist_answer" in payload["specialist_reports"][0]
    assert "template planejado" in payload["specialist_reports"][0]["final_answer"].lower()


def test_delegated_single_target_template_keeps_host_authorship():
    payload = _build_single_target_specialist_dispatch_payload(
        message="@Orion peça ao cto status ok",
        target_agent="cto",
        delegated_by="orion",
    )

    _assert_trace_lite_payload(payload)
    assert payload["visible_agent"] == "orion"
    assert payload["final_speaker"] == "orion"
    assert payload["simulated_target_agent"] == "systems_architect"
    assert payload["simulated_final_speaker"] == "systems_architect"
    assert payload["specialist_invoked"] is False
    assert payload["specialist_response_verified"] is False
    assert payload["authorship_claim"] == "not_verified"
    assert payload["delegated_by"] == "orion"


def test_controlled_self_evolution_proposal_is_planned_not_technical_execution():
    inp = OrionRuntimeIn(message="@Orion proponha evolução controlada read-only sem executar nada")
    payload = platform_self_evolution_plan(inp)

    _assert_trace_lite_payload(payload)
    assert payload["status"] == "planned"


def test_verified_evidence_can_preserve_executed_semantics():
    payload = apply_execution_evidence_to_envelope(
        {
            "event": "ORION_RUNTIME_DIAGNOSTIC_EXECUTED",
            "status": "executed",
            "execution_depth": "dispatch",
            "auditability_status": "ready_for_persistence",
            "technical_summary": "Ferramenta técnica executada com evidência completa.",
            "executive_diagnostic": "Orion executou leitura verificada do repositório.",
            "confirmed_evidence": "event=ORION_RUNTIME_DIAGNOSTIC_EXECUTED",
            "final_consolidation": "Execução confirmada por ferramenta.",
            "visible_agent": "orion",
            "final_speaker": "orion",
            "target_agent": "orion",
            "selected_specialists": ["orion"],
            "dispatch_receipts": [
                {
                    "agent": "orion",
                    "status": "executed",
                    "tool_used": "repository_readonly",
                    "tool_run_id": "run-123",
                    "repository": "backend",
                    "branch": "main",
                    "commit": "abc123",
                    "operation": "inspect_runtime",
                    "result_digest": "sha256:deadbeef",
                    "started_at": "2026-07-13T18:00:00Z",
                    "finished_at": "2026-07-13T18:00:01Z",
                    "write_executed": False,
                    "authorship_agent": "orion",
                    "authorship_verified": True,
                    "specialist_invoked": True,
                    "specialist_response_verified": True,
                }
            ],
        }
    )

    assert payload["status"] == "executed"
    assert payload["event"] == "ORION_RUNTIME_DIAGNOSTIC_EXECUTED"
    assert payload["dispatch_executed"] is True
    assert payload["execution_claim"] == "verified"
    assert payload["verification_level"] == "tool_execution"
    assert payload["execution_depth"] == "dispatch"
    assert payload["auditability_status"] == "ready_for_persistence"
    assert payload["authorship_claim"] == "verified"
    assert "executada" in payload["technical_summary"]


def test_tool_evidence_without_authorship_does_not_claim_specialist_voice():
    payload = apply_execution_evidence_to_envelope(
        {
            "event": "DIRECT_SPECIALIST_RUNTIME_EXECUTED",
            "status": "executed",
            "visible_agent": "backend_engineer",
            "final_speaker": "backend_engineer",
            "target_agent": "backend_engineer",
            "message": "Status ok. Backend operational.",
            "selected_specialists": ["backend_engineer"],
            "dispatch_receipts": [
                {
                    "agent": "repository_reader",
                    "status": "executed",
                    "tool_used": "repository_readonly",
                    "tool_run_id": "run-123",
                    "repository": "backend",
                    "branch": "main",
                    "commit": "abc123",
                    "operation": "inspect_runtime",
                    "result_digest": "sha256:deadbeef",
                    "started_at": "2026-07-13T18:00:00Z",
                    "finished_at": "2026-07-13T18:00:01Z",
                    "write_executed": False,
                }
            ],
        }
    )

    assert payload["status"] == "executed"
    assert payload["dispatch_executed"] is True
    assert payload["execution_claim"] == "verified"
    assert payload["authorship_claim"] == "not_verified"
    assert payload["specialist_invoked"] is False
    assert payload["specialist_response_verified"] is False
    assert payload["visible_agent"] == "orion"
    assert payload["final_speaker"] == "orion"
    assert payload["simulated_target_agent"] == "backend_engineer"
    assert "backend operational" not in payload["message"].lower()


def test_tool_evidence_with_target_authorship_can_claim_specialist_voice():
    payload = apply_execution_evidence_to_envelope(
        {
            "event": "DIRECT_SPECIALIST_RUNTIME_EXECUTED",
            "status": "executed",
            "visible_agent": "backend_engineer",
            "final_speaker": "backend_engineer",
            "target_agent": "backend_engineer",
            "message": "Status ok. Backend operational.",
            "selected_specialists": ["backend_engineer"],
            "dispatch_receipts": [
                {
                    "agent": "backend_engineer",
                    "status": "executed",
                    "tool_used": "specialist_runtime",
                    "tool_run_id": "run-123",
                    "repository": "backend",
                    "branch": "main",
                    "commit": "abc123",
                    "operation": "specialist_response",
                    "result_digest": "sha256:deadbeef",
                    "started_at": "2026-07-13T18:00:00Z",
                    "finished_at": "2026-07-13T18:00:01Z",
                    "write_executed": False,
                    "authorship_agent": "backend_engineer",
                    "authorship_verified": True,
                    "specialist_invoked": True,
                    "specialist_response_verified": True,
                }
            ],
        }
    )

    assert payload["status"] == "executed"
    assert payload["dispatch_executed"] is True
    assert payload["authorship_claim"] == "verified"
    assert payload["specialist_invoked"] is True
    assert payload["specialist_response_verified"] is True
    assert payload["visible_agent"] == "backend_engineer"
    assert payload["final_speaker"] == "backend_engineer"
    assert payload["message"] == "Status ok. Backend operational."


def test_all_known_persistable_fields_are_canonical_in_trace_lite():
    payload = apply_execution_evidence_to_envelope(
        {
            "event": "PLATFORM_SELF_AUDIT_DISPATCH_EXECUTED",
            "status": "executed",
            "execution_depth": "dispatch",
            "auditability_status": "ready_for_persistence",
            "technical_summary": "Dispatch interno executado em modo somente leitura.",
            "executive_diagnostic": "Orion executou diagnóstico técnico.",
            "backend_assessment": "Backend assessment com execução confirmada.",
            "frontend_assessment": "Frontend assessment com dispatch real.",
            "integration_assessment": "Integration assessment executada.",
            "confirmed_evidence": "event=ORION_RUNTIME_DIAGNOSTIC_EXECUTED",
            "main_risk": "Risco derivado de dispatch confirmado.",
            "recommended_actions": ["Renderizar execution_depth=dispatch como resposta principal."],
            "final_consolidation": "Execução confirmada.",
            "architecture_notes": ["Dispatch executado precisa ser refletido."],
            "remediation_plan": ["Emitir ORION_RUNTIME_DIAGNOSTIC_EXECUTED."],
            "findings_by_specialty": {"backend": "executado"},
            "audit_plan": {"event": "PLATFORM_SELF_AUDIT_DISPATCH_EXECUTED"},
            "persistable_sections": [
                "technical_summary",
                "executive_diagnostic",
                "backend_assessment",
                "frontend_assessment",
                "integration_assessment",
                "confirmed_evidence",
                "main_risk",
                "recommended_actions",
                "final_consolidation",
            ],
            "selected_specialists": ["orion", "cto"],
            "dispatch_receipts": [],
            "specialist_reports": [{"agent": "cto", "final_answer": "executado"}],
        }
    )

    _assert_trace_lite_payload(payload)
    assert payload["backend_assessment"].startswith("Avaliacao preliminar em trace-lite")
    assert payload["integration_assessment"].startswith("Avaliacao preliminar em trace-lite")
    assert payload["findings_by_specialty"]["status"] == "trace_lite_not_verified"
    assert payload["persistable_sections"] == [
        "technical_summary",
        "executive_diagnostic",
        "backend_assessment",
        "frontend_assessment",
        "integration_assessment",
        "confirmed_evidence",
        "main_risk",
        "recommended_actions",
        "selected_specialists",
        "dispatch_receipts",
        "dispatch_receipts_appendix",
        "specialist_reports",
        "specialist_reports_appendix",
        "frontend_render_cards",
        "team_technical_audit",
        "final_consolidation",
    ]


def test_general_multiagent_trace_lite_does_not_create_orion_as_specialist_target():
    payload = apply_execution_evidence_to_envelope(
        {
            "event": "PLATFORM_SELF_AUDIT_READY",
            "status": "ready",
            "mode": "platform_self_audit",
            "visible_agent": "orion",
            "selected_specialists": ["orion", "auditor", "cto"],
            "dispatch_receipts": [],
            "message": "Auditoria preparada.",
        }
    )

    assert payload["status"] == "ready"
    assert payload["visible_agent"] == "orion"
    assert payload["final_speaker"] == "orion"
    assert "simulated_target_agent" not in payload
    assert "simulated_final_speaker" not in payload
    assert "especialista orion" not in payload["message"].lower()
    assert "nenhum especialista-alvo" in payload["message"].lower()
    assert payload["authorship_status"] == "orchestrator_trace_lite_not_verified"


def test_non_conclusive_statuses_are_preserved_without_evidence():
    for status in ["ready", "planned", "blocked", "denied", "error", "cancelled", "canceled"]:
        payload = apply_execution_evidence_to_envelope(
            {
                "event": "PLATFORM_SELF_AUDIT_READY",
                "status": status,
                "mode": "platform_self_audit",
                "visible_agent": "orion",
                "dispatch_receipts": [],
            }
        )

        assert payload["status"] == status
        assert payload.get("original_status") in {None, ""}


def test_conclusive_statuses_are_downgraded_without_evidence():
    for status in ["executed", "completed", "success", "succeeded", "done"]:
        payload = apply_execution_evidence_to_envelope(
            {
                "event": "PLATFORM_SELF_AUDIT_DISPATCH_EXECUTED",
                "status": status,
                "mode": "platform_self_audit",
                "visible_agent": "orion",
                "dispatch_receipts": [],
            }
        )

        assert payload["status"] == "simulated"
        assert payload["original_status"] == status
        assert not payload["event"].endswith("_EXECUTED")
