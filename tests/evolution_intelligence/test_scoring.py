from app.evolution.intelligence.scoring import build_project_health_preview


def _metric(key, score, confidence=90, sample=100, status="measured"):
    return {
        "key": key,
        "score": score,
        "confidence": confidence,
        "sample_count": sample,
        "signal_status": status,
        "source": ["test"],
        "summary": f"{key} summary",
        "formula_version": "test-v1",
        "missing_sources": [],
    }


def test_missing_product_dimension_is_reported_not_green():
    snapshot = {
        "org_slug": "tenant-a",
        "generated_at": 100,
        "metrics": [
            _metric("security_governance", 100),
            _metric("operational_reliability", 99),
            _metric("governed_autoevolution", 100),
            _metric("agent_knowledge", 90),
            _metric("core_modules", 95),
            _metric("evidence_observability", 98),
            _metric("premium_experience", 90),
        ],
    }
    health = build_project_health_preview(snapshot)
    assert "product" in health["missing_dimensions"]
    assert health["coverage"] == 0.85
    assert health["health_coverage"] == 0.85
    assert health["coverage_status"] == "partial"
    assert health["unknown_kpis"] == []
    assert health["stale_kpis"] == []
    assert health["score"] is not None
    assert health["write_executed"] is False


def test_blocker_cannot_be_compensated_by_average():
    snapshot = {
        "org_slug": "tenant-a",
        "generated_at": 100,
        "metrics": [
            _metric("security_governance", 10),
            _metric("operational_reliability", 100),
            _metric("governed_autoevolution", 100),
            _metric("agent_knowledge", 100),
            _metric("core_modules", 100),
            _metric("evidence_observability", 100),
            _metric("premium_experience", 100),
        ],
    }
    health = build_project_health_preview(snapshot)
    assert health["status"] == "blocker"
    assert health["production_go"] is False
    assert "security_governance" in health["blocker_kpis"]
    assert health["blockers"] == health["blocker_kpis"]


def test_low_sample_is_insufficient_data():
    snapshot = {
        "org_slug": "tenant-a",
        "generated_at": 100,
        "metrics": [_metric("operational_reliability", 99, sample=1)],
    }
    health = build_project_health_preview(snapshot)
    item = health["kpis"][0]
    assert item["status"] == "insufficient_data"
    assert "operational_reliability" in health["missing_kpis"]
    assert item["collector_version"] == "ORKIO-EVOLUTION-COLLECTORS-R2"
    assert item["source_version"] == "ORKIO-EVOLUTION-SOURCES-R2"
