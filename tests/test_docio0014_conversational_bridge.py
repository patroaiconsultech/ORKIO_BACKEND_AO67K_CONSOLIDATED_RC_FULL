from __future__ import annotations

import logging
import sys
import types
import uuid
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


ROOT = Path(__file__).resolve().parents[1]
app_alias = sys.modules.get("app")
if app_alias is None:
    app_alias = types.ModuleType("app")
    app_alias.__path__ = [str(ROOT / "app"), str(ROOT)]  # type: ignore[attr-defined]
    sys.modules["app"] = app_alias

from app.db import Base
from app.models import AuditLog, File, Message, Thread
from app.runtime.capability_registry import (
    CAPABILITY_EXECUTION_BINDINGS,
    CAPABILITY_METADATA,
    CAPABILITY_REGISTRY,
    GOVERNED_CAPABILITY_PROFILES,
)
from app.runtime.document_artifact_intent import (
    artifact_success_message,
    build_document_artifact_payload,
    classify_document_artifact_request,
)
from app.schemas.document_artifacts import DocumentArtifactGenerateIn
from app.services.document_artifact_command_service import (
    DocumentArtifactCommandDeps,
    execute_document_artifact_command,
)
from app.services.document_artifact_service import generate_document_artifact


def _database():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, autoflush=False, autocommit=False)


def test_explicit_orion_spreadsheet_request_is_executable():
    decision = classify_document_artifact_request(
        "Orion, gere uma planilha de teste, por favor.",
        agent_slug="orion",
    )
    assert decision == {
        "handled": True,
        "capability": "document_artifact_generate",
        "format": "xlsx",
        "agent_slug": "orion",
        "reason": "explicit_document_artifact_request",
        "write_kind": "user_requested_artifact",
        "human_approval_required": False,
    }


def test_instructional_request_stays_conversational():
    decision = classify_document_artifact_request(
        "Orion, me ensine como criar uma planilha.",
        agent_slug="orion",
    )
    assert decision["handled"] is False
    assert decision["reason"] == "instructional_request"


def test_non_authorized_agent_does_not_claim_document_execution():
    decision = classify_document_artifact_request(
        "Chris, gere uma planilha de teste.",
        agent_slug="chris",
    )
    assert decision["handled"] is False
    assert decision["reason"] == "agent_not_allowed_for_document_generation"


def test_payload_builder_produces_bounded_xlsx_rows():
    decision = classify_document_artifact_request(
        "Orion, gere uma planilha de teste com colunas: cliente, status e valor.",
        agent_slug="orion",
    )
    payload = build_document_artifact_payload(
        "Orion, gere uma planilha de teste com colunas: cliente, status e valor.",
        decision,
        thread_id="thread-a",
        requested_agent_hint="orion",
    )
    model = DocumentArtifactGenerateIn.model_validate(payload)
    assert model.format == "xlsx"
    assert model.thread_id == "thread-a"
    assert model.requested_agent_hint == "orion"
    assert model.rows
    assert model.rows[0] == ["Cliente", "Status", "Valor"]


def test_command_service_persists_artifact_event_assistant_and_audit_atomically():
    engine, factory = _database()
    try:
        with factory() as db:
            db.add(
                Thread(
                    id="thread-a",
                    org_slug="org-a",
                    title="Teste",
                    created_at=1_720_000_000,
                )
            )
            db.commit()

        decision = classify_document_artifact_request(
            "Orion, gere uma planilha de teste.",
            agent_slug="orion",
        )
        input_model = DocumentArtifactGenerateIn.model_validate(
            build_document_artifact_payload(
                "Orion, gere uma planilha de teste.",
                decision,
                thread_id="thread-a",
                requested_agent_hint="orion",
            )
        )

        with factory() as db:
            result = execute_document_artifact_command(
                db,
                input_model=input_model,
                org="org-a",
                user={
                    "sub": "user-a",
                    "name": "Daniel",
                    "email": "daniel@example.test",
                    "role": "admin",
                },
                request_id="trace-a",
                path="/api/chat/stream",
                deps=DocumentArtifactCommandDeps(
                    new_id=lambda: uuid.uuid4().hex,
                    now_ts=lambda: 1_720_000_100,
                    logger=logging.getLogger("docio0014-test"),
                    generate_artifact=lambda payload, limits=None: generate_document_artifact(
                        payload,
                        limits=limits,
                    ),
                ),
                resolved_agent_id="orion-id",
                resolved_agent_name="Orion",
                assistant_text_builder=lambda artifact: artifact_success_message(
                    agent_name="Orion",
                    filename=artifact["filename"],
                ),
                authorship_claim="immutable_turn_owner",
            )

        assert result["ok"] is True
        assert result["format"] == "xlsx"
        assert result["artifact"]["capability"] == "document_artifact_generate"
        assert result["assistant_persisted"] is True
        assert result["thread_event_persisted"] is True
        assert result["audit_persisted"] is True

        with factory() as db:
            files = db.execute(select(File)).scalars().all()
            messages = db.execute(
                select(Message).where(Message.thread_id == "thread-a")
            ).scalars().all()
            audits = db.execute(
                select(AuditLog).where(
                    AuditLog.action == "document_artifact.generated"
                )
            ).scalars().all()

        assert len(files) == 1
        assert files[0].content
        assert any(message.role == "system" and "ORKIO_EVENT:" in message.content for message in messages)
        assert any(message.role == "assistant" and "Baixar arquivo" in message.content for message in messages)
        assert len(audits) == 1
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_capability_registry_declares_governed_document_execution():
    capability = "document_artifact_generate"
    assert CAPABILITY_METADATA[capability]["governed"] is True
    assert CAPABILITY_EXECUTION_BINDINGS[capability]["write"] is True
    assert CAPABILITY_EXECUTION_BINDINGS[capability]["human_approval_required"] is False
    assert GOVERNED_CAPABILITY_PROFILES[capability]["allowed_targets"] == [
        "user_artifact",
        "thread",
    ]
    assert capability in CAPABILITY_REGISTRY["orkio"]["capabilities"]
    assert capability in CAPABILITY_REGISTRY["orion"]["capabilities"]


def test_bridge_precedes_stream_lite_and_emits_artifacts_in_done():
    source = (ROOT / "main.py").read_text(encoding="utf-8-sig")
    bridge_at = source.index("DOCIO-001.4 — Conversational Artifact Execution Bridge")
    stream_lite_at = source.index("P0-RS01_STREAM_LITE_RUNTIME_STABILIZER")
    assert bridge_at < stream_lite_at
    assert '"artifact": payload.get("artifact")' in source
    assert '"artifacts": payload.get("artifacts") or []' in source
    assert '"execution_lifecycle": "failed"' in source
    assert "DOCIO_ARTIFACT_GENERATION_FAILED" in source
