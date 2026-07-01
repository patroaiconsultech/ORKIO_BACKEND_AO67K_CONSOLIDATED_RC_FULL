from platform_services.eos_health import get_eos_health_snapshot


def test_eos_health_snapshot_readonly():
    data = get_eos_health_snapshot()

    assert data["version"] == "EOS_HEALTH_V1"
    assert data["status"] == "foundation_active"
    assert data["readonly"] is True
    assert data["write_executed"] is False
    assert set(data["scores"].keys()) == {
        "platform",
        "knowledge",
        "architecture",
        "governance",
        "product",
    }
