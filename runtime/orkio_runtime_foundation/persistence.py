"""
ORKIO CORE RC-1 / EPIC-002B
Runtime Persistence Canonical Assistant Message ID — Shadow Locked

Status:
    shadow_only
    no database writes
    no runtime integration
    no SSE integration
    no production side effects

Purpose:
    Close EPIC-002B by making the Runtime Persistence Layer the single
    authority for assistant_message_id identity.

Canonical identity:
    thread_id + turn_id + user_message_id

Canonical assistant_message_id:
    deterministic SHA-256 derived inside this module from the canonical identity.

Important:
    Callers MUST NOT provide assistant_message_id.
    trace_id is observability metadata only.
    request_id, timestamp, agent_id, trace_id and other mutable transport fields
    MUST NOT participate in canonical identity derivation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import RLock
from typing import Mapping, MutableMapping, Optional, Tuple
import hashlib
import json


ASSISTANT_MESSAGE_ID_PREFIX = "asstmsg"


class PersistenceStatus(str, Enum):
    CREATED = "created"
    DUPLICATE_BLOCKED = "duplicate_blocked"
    CONFLICT_BLOCKED = "conflict_blocked"
    ROLLED_BACK = "rolled_back"
    ROLLBACK_NOOP = "rollback_noop"


class ShadowOnlyViolation(RuntimeError):
    """Raised when EPIC-002B is asked to perform non-shadow persistence."""


class ExternalAssistantMessageIdViolation(ValueError):
    """Raised when a caller attempts to supply assistant_message_id externally."""


@dataclass(frozen=True)
class PersistenceIdentity:
    """Stable logical identity of one assistant response finalization."""

    thread_id: str
    turn_id: str
    user_message_id: str

    def canonical_tuple(self) -> Tuple[str, str, str]:
        return (
            _normalize_required(self.thread_id, "thread_id"),
            _normalize_required(self.turn_id, "turn_id"),
            _normalize_required(self.user_message_id, "user_message_id"),
        )

    def canonical_payload(self) -> str:
        """
        Serialize canonical identity without delimiter ambiguity.

        JSON compact serialization is used with explicit field names and stable
        key ordering so values such as ("a|b", "c", "d") and ("a", "b|c", "d")
        cannot collide.
        """
        thread_id, turn_id, user_message_id = self.canonical_tuple()
        return json.dumps(
            {
                "thread_id": thread_id,
                "turn_id": turn_id,
                "user_message_id": user_message_id,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def idempotency_key(self) -> str:
        raw = self.canonical_payload()
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def assistant_message_id(self) -> str:
        """
        Deterministically derive the canonical assistant message id.

        The id is intentionally derived from the same stable tuple as the
        idempotency key, with a fixed namespace prefix to make the value
        self-describing while preserving deterministic replay.
        """
        return f"{ASSISTANT_MESSAGE_ID_PREFIX}_{self.idempotency_key()}"


@dataclass(frozen=True)
class PersistenceObservation:
    """Non-authoritative observability metadata for the persistence attempt."""

    trace_id: str = ""
    source: str = "runtime_persistence_shadow"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True, init=False)
class AssistantCommit:
    """
    A shadow record for a future assistant finalization commit.

    assistant_message_id is always derived internally. This class intentionally
    uses init=False to prevent callers from passing assistant_message_id into the
    constructor.
    """

    identity: PersistenceIdentity
    response_hash: str
    observation: PersistenceObservation
    assistant_message_id: str

    def __init__(
        self,
        *,
        identity: PersistenceIdentity,
        response_hash: str,
        observation: Optional[PersistenceObservation] = None,
    ) -> None:
        object.__setattr__(self, "identity", identity)
        object.__setattr__(self, "response_hash", _normalize_required(response_hash, "response_hash"))
        object.__setattr__(self, "observation", observation or PersistenceObservation())
        object.__setattr__(self, "assistant_message_id", identity.assistant_message_id())

    @classmethod
    def from_external_assistant_message_id(
        cls,
        *,
        identity: PersistenceIdentity,
        assistant_message_id: str,
        response_hash: str,
        observation: Optional[PersistenceObservation] = None,
    ) -> "AssistantCommit":
        """
        Explicit rejection path for compatibility audits.

        This method exists only so tests and migration audits can prove that
        EPIC-002B refuses externally supplied assistant_message_id values.
        """
        raise ExternalAssistantMessageIdViolation(
            "assistant_message_id is owned by Runtime Persistence Layer and must be derived internally"
        )

    @property
    def idempotency_key(self) -> str:
        return self.identity.idempotency_key()


@dataclass(frozen=True)
class PersistenceResult:
    status: PersistenceStatus
    idempotency_key: str
    assistant_message_id: str
    existing_assistant_message_id: Optional[str] = None
    reason: str = ""


def build_response_hash(response_text: str) -> str:
    normalized = (response_text or "").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


class RuntimePersistenceShadowLedger:
    """
    In-memory shadow ledger for canonical persistence idempotency.

    This class is intentionally isolated. It does not write to a database,
    does not emit SSE events, and does not integrate with production runtime.

    Thread safety:
        commit(), rollback(), preview_key(), preview_assistant_message_id()
        and snapshot() are protected by an RLock so SHADOW concurrency tests can
        validate deterministic duplicate blocking without introducing a second
        authority.
    """

    def __init__(self, *, shadow_only: bool = True) -> None:
        if shadow_only is not True:
            raise ShadowOnlyViolation(
                "EPIC-002B is shadow-only. Non-shadow persistence is forbidden in this phase."
            )
        self._records: MutableMapping[str, AssistantCommit] = {}
        self._lock = RLock()

    def preview_key(self, identity: PersistenceIdentity) -> str:
        with self._lock:
            return identity.idempotency_key()

    def preview_assistant_message_id(self, identity: PersistenceIdentity) -> str:
        with self._lock:
            return identity.assistant_message_id()

    def commit(self, commit: AssistantCommit) -> PersistenceResult:
        key = commit.idempotency_key
        expected_assistant_message_id = commit.identity.assistant_message_id()

        if commit.assistant_message_id != expected_assistant_message_id:
            raise ExternalAssistantMessageIdViolation(
                "assistant_message_id mismatch: commit identity is not canonical"
            )

        with self._lock:
            existing = self._records.get(key)

            if existing is None:
                self._records[key] = commit
                return PersistenceResult(
                    status=PersistenceStatus.CREATED,
                    idempotency_key=key,
                    assistant_message_id=commit.assistant_message_id,
                    reason="shadow_canonical_record_created",
                )

            if (
                existing.assistant_message_id == commit.assistant_message_id
                and existing.response_hash == commit.response_hash
            ):
                return PersistenceResult(
                    status=PersistenceStatus.DUPLICATE_BLOCKED,
                    idempotency_key=key,
                    assistant_message_id=commit.assistant_message_id,
                    existing_assistant_message_id=existing.assistant_message_id,
                    reason="same_logical_turn_already_recorded",
                )

            return PersistenceResult(
                status=PersistenceStatus.CONFLICT_BLOCKED,
                idempotency_key=key,
                assistant_message_id=commit.assistant_message_id,
                existing_assistant_message_id=existing.assistant_message_id,
                reason="same_logical_turn_conflicting_response_blocked",
            )

    def rollback(self, identity: PersistenceIdentity) -> PersistenceResult:
        key = identity.idempotency_key()
        assistant_message_id = identity.assistant_message_id()

        with self._lock:
            existing = self._records.pop(key, None)

            if existing is None:
                return PersistenceResult(
                    status=PersistenceStatus.ROLLBACK_NOOP,
                    idempotency_key=key,
                    assistant_message_id=assistant_message_id,
                    reason="shadow_record_not_found",
                )

            return PersistenceResult(
                status=PersistenceStatus.ROLLED_BACK,
                idempotency_key=key,
                assistant_message_id=existing.assistant_message_id,
                existing_assistant_message_id=existing.assistant_message_id,
                reason="shadow_record_removed",
            )

    def snapshot(self) -> Mapping[str, AssistantCommit]:
        with self._lock:
            return dict(self._records)


def _normalize_required(value: str, field_name: str) -> str:
    normalized = (value or "").strip()
    if not normalized:
        raise ValueError(f"{field_name} is required for canonical persistence identity")
    return normalized
