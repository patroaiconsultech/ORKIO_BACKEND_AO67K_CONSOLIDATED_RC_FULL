from app.evolution.intelligence.diagnostics import build_diagnostic_preview
from app.evolution.intelligence.prioritization import build_priority_preview
from app.services.evolution_intelligence_service import build_proposal_previews


def _health(confidence=0.9, status="critical"):
    return {
        "org_slug": "tenant-a",
        "kpis": [
            {
                "code": "operational_reliability",
                "status": status,
                "confidence": confidence,
                "summary": "5 falhas em 100 execuções.",
                "source": ["admin_evolution_executions"],
                "blocker": False,
            }
        ],
    }


def test_diagnostic_separates_evidence_from_hypothesis():
    result = build_diagnostic_preview(_health())
    item = result["items"][0]
    assert item["evidence"][0]["classification"] == "evidência confirmada"
    assert item["hypotheses"][0]["classification"] == "hipótese prioritária"
    assert item["root_cause_status"] == "not_confirmed"
    assert item["recommended_action"] == "technical_proposal_allowed"


def test_low_confidence_does_not_generate_technical_proposal():
    diagnostics = build_diagnostic_preview(_health(confidence=0.4))
    priorities = build_priority_preview(_health(confidence=0.4))
    proposals = build_proposal_previews(
        diagnostics,
        priorities,
        objective_id=None,
    )
    assert proposals["count"] == 0
    assert proposals["write_executed"] is False


def test_preview_never_enables_auto_apply():
    health = _health()
    diagnostics = build_diagnostic_preview(health)
    priorities = build_priority_preview(health)
    proposals = build_proposal_previews(
        diagnostics,
        priorities,
        objective_id="obj-1",
    )
    assert proposals["count"] == 1
    assert proposals["items"][0]["auto_apply"] is False
    assert proposals["items"][0]["mode"] == "proposal_only"
