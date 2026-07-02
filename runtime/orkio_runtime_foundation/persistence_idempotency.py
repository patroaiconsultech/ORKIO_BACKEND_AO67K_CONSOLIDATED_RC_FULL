import logging
from dataclasses import dataclass, field
from typing import Set

logger = logging.getLogger("orkio.persistence_idempotency")

@dataclass
class PersistenceIdempotencyGuard:
    seen: Set[str] = field(default_factory=set)

    def build_key(self, trace_id: str, thread_id: str, assistant_turn_id: str) -> str:
        return f"{trace_id}:{thread_id}:{assistant_turn_id}"

    def should_persist(self, key: str) -> bool:
        if key in self.seen:
            logger.warning("ASSISTANT_PERSIST_SKIPPED_DUPLICATE key=%s", key)
            return False
        logger.info("ASSISTANT_PERSIST_ATTEMPT key=%s", key)
        return True

    def mark_persisted(self, key: str) -> None:
        self.seen.add(key)
        logger.info("ASSISTANT_PERSIST_CREATED key=%s", key)
