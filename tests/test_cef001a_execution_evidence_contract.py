from pathlib import Path

from runtime.execution_evidence_contract import (
    apply_execution_evidence_to_envelope,
    build_trace_lite_receipt,
    has_verified_execution_evidence,
    normalize_execution_receipt,
    readonly_governance_fields,
)


def test_static_receipt_is_trace_lite_not_executed():
    receipt = build_trace_lite_receipt(
        agent="orion",
        mode="read_only_dispatch",
        scope="platform",
        deliverable="architecture analysis",
        generated_at=123,
    )

    assert receipt["status"] == "simulated"
    assert receipt["evidence_verified"] is False
    assert receipt["verification_level"] == "trace_lite"
    assert receipt["execution_claim"] == "not_verified"
    assert receipt["write_executed"] is False


def test_executed_without_evidence_is_downgraded():
    receipt = normalize_execution_receipt(
        {
            "agent": "orion",
            "status": "executed",
            "write_executed": False,
        }
    )

    assert receipt["original_status"] == "executed"
    assert receipt["status"] == "simulated"
    assert receipt["evidence_verified"] is False


def test_complete_tool_evidence_can_be_executed():
    receipt = {
        "agent": "orion",
        "status": "executed",
        "tool_used": "repository_readonly",
        "tool_run_id": "run-123",
        "repository": "backend",
        "branch": "main",
        "commit": "abc123",
        "operation": "list_tree",
        "result_digest": "sha256:deadbeef",
        "started_at": "2026-07-13T18:00:00Z",
        "finished_at": "2026-07-13T18:00:01Z",
        "write_executed": False,
    }

    assert has_verified_execution_evidence(receipt)
    normalized = normalize_execution_receipt(receipt)
    assert normalized["status"] == "executed"
    assert normalized["evidence_verified"] is True
    assert normalized["verification_level"] == "tool_execution"


def test_trace_lite_receipts_do_not_produce_executed_envelope():
    payload = apply_execution_evidence_to_envelope(
        {
            "event": "PLATFORM_SELF_AUDIT_DISPATCH_EXECUTED",
            "status": "executed",
            "selected_specialists": ["orion", "cto"],
            "dispatch_receipts": [
                build_trace_lite_receipt(
                    agent="orion",
                    mode="read_only_dispatch",
                    scope="platform",
                    deliverable="readonly diagnostic",
                    generated_at=123,
                )
            ],
        }
    )

    assert payload["status"] == "simulated"
    assert payload["original_status"] == "executed"
    assert payload["event"] == "PLATFORM_SELF_AUDIT_DISPATCH_TRACE_LITE"
    assert not payload["event"].endswith("_EXECUTED")
    assert payload["dispatch_executed"] is False
    assert payload["execution_claim"] == "not_verified"
    assert payload["verification_level"] == "trace_lite"
    assert payload["specialists_selected"] is True
    assert payload["specialists_selected_count"] == 2


def test_specialist_selection_without_tool_evidence_is_not_dispatch_executed():
    payload = apply_execution_evidence_to_envelope(
        {
            "event": "ORION_RUNTIME_DIAGNOSTIC_EXECUTED",
            "status": "executed",
            "selected_specialists": ["orion"],
            "dispatch_receipts": [],
        }
    )

    assert payload["specialists_selected"] is True
    assert payload["dispatch_executed"] is False
    assert payload["execution_claim"] == "not_verified"


def test_complete_tool_evidence_can_produce_executed_envelope():
    payload = apply_execution_evidence_to_envelope(
        {
            "event": "ORION_RUNTIME_DIAGNOSTIC_EXECUTED",
            "status": "executed",
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
                    "operation": "inspect_routes",
                    "result_digest": "sha256:deadbeef",
                    "started_at": "2026-07-13T18:00:00Z",
                    "finished_at": "2026-07-13T18:00:01Z",
                    "write_executed": False,
                }
            ],
        }
    )

    assert payload["status"] == "executed"
    assert payload["event"] == "ORION_RUNTIME_DIAGNOSTIC_EXECUTED"
    assert payload["dispatch_executed"] is True
    assert payload["execution_claim"] == "verified"
    assert payload["verification_level"] == "tool_execution"
    assert payload["verified_execution_count"] == 1


def test_readonly_governance_fields_are_fail_closed():
    fields = readonly_governance_fields()

    assert fields == {
        "write_allowed": False,
        "proposal_created": False,
        "proposal_only": False,
        "commit_executed": False,
        "merge_executed": False,
        "deploy_executed": False,
        "migration_executed": False,
        "human_approval_required": True,
    }


def test_orion_internal_uses_trace_lite_builder():
    root = Path(__file__).resolve().parents[1]
    source = (root / "routes/internal/orion_internal.py").read_text(encoding="utf-8")
    assert "build_trace_lite_receipt(" in source
    assert '"status": "executed",\n            "mode": "read_only_dispatch"' not in source
    assert "apply_execution_evidence_to_envelope(" in source
    assert "dispatch_executed=True" not in source


def test_main_uses_explicit_ux_guard_without_new_business_logic():
    root = Path(__file__).resolve().parents[1]
    source = (root / "main.py").read_text(encoding="utf-8")
    assert "wants_ux = is_explicit_ux_audit_request(raw)" in source
