from app.evolution.intelligence.kpi_registry import (
    PROJECT_HEALTH_WEIGHTS,
    registry_payload,
)


def test_registry_is_complete_and_auto_apply_is_disabled():
    payload = registry_payload()
    assert payload["registry_version"] == "ORKIO-EVOLUTION-KPI-REGISTRY-R2"
    assert payload["count"] == 7
    assert payload["definition_incomplete"] == []
    assert payload["definition_complete_count"] == payload["count"]
    assert payload["auto_apply_enabled"] is False
    assert round(sum(PROJECT_HEALTH_WEIGHTS.values()), 6) == 1.0
    for definition in payload["definitions"]:
        assert definition["definition_status"] == "complete"
        assert definition["auto_apply_enabled"] is False
        assert definition["allowed_actions"]
        assert definition["forbidden_actions"]
