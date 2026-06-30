from platform_services.metrics import MetricsRegistry, Timer


def test_metrics_registry():
    registry = MetricsRegistry()
    registry.increment("chat.requests")
    registry.increment("chat.requests", amount=2)
    registry.gauge("queue.depth", 3)
    registry.observe_ms("llm.latency", 10)
    registry.observe_ms("llm.latency", 20)

    snapshot = registry.snapshot()
    assert snapshot["total"] == 3

    timer_metrics = [item for item in snapshot["metrics"] if item["name"] == "llm.latency"]
    assert timer_metrics[0]["avg_ms"] == 15


def test_timer_context_manager():
    registry = MetricsRegistry()
    with Timer(registry, "operation.duration"):
        sum(range(10))
    snapshot = registry.snapshot()
    assert snapshot["total"] == 1
    assert snapshot["metrics"][0]["count"] == 1


if __name__ == "__main__":
    test_metrics_registry()
    test_timer_context_manager()
    print("OEP010_2_METRICS_SMOKE_PASS")
