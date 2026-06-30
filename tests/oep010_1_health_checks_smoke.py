from platform_services.health_checks import (
    HealthCheckRegistry,
    HealthCheckResult,
    HealthStatus,
    run_default_health_checks,
    summarize_health,
)


def test_default_health_checks():
    summary = run_default_health_checks()
    assert summary["overall_status"] == "healthy"
    assert summary["healthy"] >= 1


def test_registry_catches_unhealthy_exception():
    registry = HealthCheckRegistry()

    def broken():
        raise RuntimeError("boom")

    registry.register("broken", broken)
    results = registry.run_all()
    summary = summarize_health(results)
    assert summary["overall_status"] == "unhealthy"
    assert summary["unhealthy"] == 1


if __name__ == "__main__":
    test_default_health_checks()
    test_registry_catches_unhealthy_exception()
    print("OEP010_1_HEALTH_CHECKS_SMOKE_PASS")
