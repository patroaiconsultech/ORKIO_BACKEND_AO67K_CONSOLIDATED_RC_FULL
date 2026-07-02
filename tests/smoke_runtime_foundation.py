from runtime.orkio_runtime_foundation import PersistenceIdempotencyGuard, TerminalGuardV7Trace

def main() -> None:
    guard = PersistenceIdempotencyGuard()
    key = guard.build_key("trace1", "thread1", "turn1")
    assert guard.should_persist(key) is True
    guard.mark_persisted(key)
    assert guard.should_persist(key) is False

    t = TerminalGuardV7Trace(trace_id="trace1", thread_id="thread1")
    t.open()
    t.first_status()
    t.kernel_ready("test")
    t.persisted("msg1")
    t.done()
    t.unlock()
    assert "unlock" in t.events
    print("SMOKE_RUNTIME_FOUNDATION_OK")

if __name__ == "__main__":
    main()
