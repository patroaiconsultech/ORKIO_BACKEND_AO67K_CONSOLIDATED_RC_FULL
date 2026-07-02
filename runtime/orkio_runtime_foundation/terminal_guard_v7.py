import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any

logger = logging.getLogger("orkio.terminal_guard_v7")

@dataclass
class TerminalGuardV7Trace:
    trace_id: str
    thread_id: str
    message_id: str | None = None
    opened_at: float = field(default_factory=time.time)
    events: Dict[str, float] = field(default_factory=dict)

    def mark(self, event: str, **extra: Any) -> None:
        now = time.time()
        self.events[event] = now
        elapsed_ms = int((now - self.opened_at) * 1000)
        logger.info(
            "TERMINAL_GUARD_V7_%s trace_id=%s thread_id=%s message_id=%s elapsed_ms=%s extra=%s",
            event.upper(),
            self.trace_id,
            self.thread_id,
            self.message_id,
            elapsed_ms,
            extra,
        )

    def open(self) -> None:
        self.mark("open")

    def first_status(self) -> None:
        self.mark("first_status")

    def first_chunk(self) -> None:
        self.mark("first_chunk")

    def kernel_ready(self, category: str) -> None:
        self.mark("kernel_ready", category=category)

    def persisted(self, assistant_message_id: str | None = None) -> None:
        if assistant_message_id:
            self.message_id = assistant_message_id
        self.mark("persisted")

    def done(self) -> None:
        self.mark("done")

    def unlock(self) -> None:
        self.mark("unlock")
