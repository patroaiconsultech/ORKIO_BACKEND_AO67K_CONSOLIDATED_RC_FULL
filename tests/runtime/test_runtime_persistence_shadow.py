from concurrent.futures import ThreadPoolExecutor

import pytest

from runtime.orkio_runtime_foundation.persistence import (
    ASSISTANT_MESSAGE_ID_PREFIX,
    AssistantCommit,
    ExternalAssistantMessageIdViolation,
    PersistenceIdentity,
    PersistenceObservation,
    PersistenceStatus,
    RuntimePersistenceShadowLedger,
    ShadowOnlyViolation,
    build_response_hash,
)


def _identity(
    thread_id: str = "thread-1",
    turn_id: str = "turn-1",
    user_message_id: str = "user-1",
) -> PersistenceIdentity:
    return PersistenceIdentity(
        thread_id=thread_id,
        turn_id=turn_id,
        user_message_id=user_message_id,
    )


def _commit(
    *,
    trace_id: str,
    response_text: str = "Resposta final",
    identity: PersistenceIdentity | None = None,
) -> AssistantCommit:
    return AssistantCommit(
        identity=identity or _identity(),
        response_hash=build_response_hash(response_text),
        observation=PersistenceObservation(trace_id=trace_id),
    )


def test_assistant_message_id_is_derived_deterministically_from_canonical_identity():
    identity = _identity()
    first = _commit(trace_id="trace-a", identity=identity)
    retry = _commit(trace_id="trace-b", identity=identity)

    assert first.idempotency_key == retry.idempotency_key
    assert first.assistant_message_id == retry.assistant_message_id
    assert first.assistant_message_id.startswith(f"{ASSISTANT_MESSAGE_ID_PREFIX}_")
    assert first.assistant_message_id == identity.assistant_message_id()


def test_external_assistant_message_id_is_rejected_explicitly():
    with pytest.raises(ExternalAssistantMessageIdViolation):
        AssistantCommit.from_external_assistant_message_id(
            identity=_identity(),
            assistant_message_id="assistant-external",
            response_hash=build_response_hash("Resposta final"),
            observation=PersistenceObservation(trace_id="trace-a"),
        )


def test_constructor_does_not_accept_external_assistant_message_id():
    with pytest.raises(TypeError):
        AssistantCommit(
            identity=_identity(),
            assistant_message_id="assistant-external",
            response_hash=build_response_hash("Resposta final"),
            observation=PersistenceObservation(trace_id="trace-a"),
        )


def test_canonical_key_and_assistant_id_exclude_trace_id_across_retries():
    ledger = RuntimePersistenceShadowLedger()

    first = _commit(trace_id="trace-a")
    retry = _commit(trace_id="trace-b")

    first_result = ledger.commit(first)
    retry_result = ledger.commit(retry)

    assert first_result.status == PersistenceStatus.CREATED
    assert retry_result.status == PersistenceStatus.DUPLICATE_BLOCKED
    assert retry_result.existing_assistant_message_id == first.assistant_message_id
    assert retry_result.assistant_message_id == first.assistant_message_id


def test_same_identity_with_different_response_is_conflict_blocked():
    ledger = RuntimePersistenceShadowLedger()

    first = _commit(trace_id="trace-a", response_text="Resposta final")
    conflicting = _commit(trace_id="trace-b", response_text="Resposta alterada")

    assert first.assistant_message_id == conflicting.assistant_message_id
    assert ledger.commit(first).status == PersistenceStatus.CREATED

    result = ledger.commit(conflicting)

    assert result.status == PersistenceStatus.CONFLICT_BLOCKED
    assert result.existing_assistant_message_id == first.assistant_message_id


def test_different_user_message_generates_different_key_and_different_assistant_id():
    first = _identity(user_message_id="user-1")
    second = _identity(user_message_id="user-2")

    assert first.idempotency_key() != second.idempotency_key()
    assert first.assistant_message_id() != second.assistant_message_id()



def test_canonical_serialization_has_no_delimiter_collision():
    first = _identity(thread_id="a|b", turn_id="c", user_message_id="d")
    second = _identity(thread_id="a", turn_id="b|c", user_message_id="d")

    assert first.canonical_payload() != second.canonical_payload()
    assert first.idempotency_key() != second.idempotency_key()
    assert first.assistant_message_id() != second.assistant_message_id()


def test_shadow_only_false_is_forbidden_by_construction():
    with pytest.raises(ShadowOnlyViolation):
        RuntimePersistenceShadowLedger(shadow_only=False)


def test_empty_identity_fields_are_rejected():
    identity = _identity(turn_id="")

    with pytest.raises(ValueError, match="turn_id"):
        identity.idempotency_key()


def test_concurrent_retries_create_one_record_and_block_duplicates():
    ledger = RuntimePersistenceShadowLedger()
    identity = _identity()

    def worker(index: int):
        commit = _commit(trace_id=f"trace-{index}", identity=identity)
        return ledger.commit(commit).status

    with ThreadPoolExecutor(max_workers=16) as executor:
        statuses = list(executor.map(worker, range(32)))

    assert statuses.count(PersistenceStatus.CREATED) == 1
    assert statuses.count(PersistenceStatus.DUPLICATE_BLOCKED) == 31
    assert len(ledger.snapshot()) == 1


def test_rollback_removes_shadow_record_and_is_idempotent():
    ledger = RuntimePersistenceShadowLedger()
    identity = _identity()
    commit = _commit(trace_id="trace-a", identity=identity)

    assert ledger.commit(commit).status == PersistenceStatus.CREATED

    rollback = ledger.rollback(identity)
    rollback_again = ledger.rollback(identity)

    assert rollback.status == PersistenceStatus.ROLLED_BACK
    assert rollback.assistant_message_id == identity.assistant_message_id()
    assert rollback_again.status == PersistenceStatus.ROLLBACK_NOOP
    assert len(ledger.snapshot()) == 0


def test_sse_compatibility_no_transport_fields_required_for_commit():
    commit = AssistantCommit(
        identity=_identity(),
        response_hash=build_response_hash("Resposta final"),
    )

    assert commit.observation.trace_id == ""
    assert commit.assistant_message_id == commit.identity.assistant_message_id()
