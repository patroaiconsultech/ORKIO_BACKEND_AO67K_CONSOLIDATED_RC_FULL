from platform_services.observability_events import ObservabilityEventBus


def test_event_bus_emit_and_limit():
    bus = ObservabilityEventBus(max_events=2)
    bus.emit("startup", "boot")
    bus.emit("chat", "message")
    bus.emit("done", "completed", severity="debug")

    events = bus.list_events()
    assert len(events) == 2
    assert events[-1]["event_type"] == "done"

    debug_events = bus.list_events(severity="debug")
    assert len(debug_events) == 1


if __name__ == "__main__":
    test_event_bus_emit_and_limit()
    print("OEP010_3_OBSERVABILITY_EVENTS_SMOKE_PASS")
