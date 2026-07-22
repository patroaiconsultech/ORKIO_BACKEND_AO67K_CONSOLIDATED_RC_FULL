from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.runtime.glip_aria_document_bridge import (
    GLIP_ARIA_CREATE_FORMATS,
    GLIP_ARIA_DOCUMENT_BRIDGE_VERSION,
    GLIP_ARIA_READ_FORMATS,
    GlipAriaDocumentArtifactGenerateIn,
    build_glip_aria_document_system_prompt,
    build_glip_aria_terminal_events,
    classify_glip_aria_document_request,
    merge_glip_aria_document_runtime_hints,
)
from app.schemas.document_artifacts import DocumentArtifactGenerateIn


ROOT = Path(__file__).resolve().parents[1]


def test_glip_document_formats_match_proven_backend_contract():
    assert GLIP_ARIA_READ_FORMATS == (
        "pdf",
        "docx",
        "xlsx",
        "pptx",
        "csv",
        "txt",
        "md",
    )
    assert GLIP_ARIA_CREATE_FORMATS == (
        "pdf",
        "docx",
        "xlsx",
        "pptx",
        "csv",
        "md",
    )


def test_glip_aria_classifies_explicit_creation_but_not_instructional_question():
    decision = classify_glip_aria_document_request(
        "Aria, crie um PDF com o resumo desta conversa."
    )
    assert decision["handled"] is True
    assert decision["format"] == "pdf"
    assert decision["agent_slug"] == "aria"
    assert decision["bridge_version"] == GLIP_ARIA_DOCUMENT_BRIDGE_VERSION

    instructional = classify_glip_aria_document_request(
        "Aria, como criar um PDF?"
    )
    assert instructional["handled"] is False


def test_glip_aria_respects_governance_write_blocker():
    decision = classify_glip_aria_document_request(
        "proposal_only: crie um PDF, mas não gere arquivo."
    )
    assert decision["handled"] is False
    assert decision["reason"] == "governance_write_blocked"


def test_public_schema_stays_closed_while_glip_internal_schema_accepts_source_plan():
    payload = {
        "format": "pptx",
        "title": "Apresentação GLIP",
        "content": "Conteúdo",
        "slides": [{"title": "Capa", "bullets": ["Ponto"]}],
        "source_plan": {
            "contract": "PPTX_SOURCE_PLAN_V1",
            "planned_slide_count": 1,
        },
        "requested_agent_hint": "aria",
    }

    with pytest.raises(ValidationError):
        DocumentArtifactGenerateIn.model_validate(payload)

    trusted = GlipAriaDocumentArtifactGenerateIn.model_validate(payload)
    assert trusted.source_plan["contract"] == "PPTX_SOURCE_PLAN_V1"
    assert trusted.requested_agent_hint == "aria"


def test_document_prompt_injects_authorized_context_without_changing_empty_prompt():
    base = "Você é Aria."
    assert build_glip_aria_document_system_prompt(base, {}) == base

    prompt = build_glip_aria_document_system_prompt(
        base,
        {
            "context_available": True,
            "file_context_block": (
                "DOCUMENTOS ANEXADOS À THREAD — CONTEXTO AUTORIZADO:\n"
                "[Arquivo: briefing.pdf]\nÁrea: 120 m²"
            ),
        },
    )
    assert prompt.startswith(base)
    assert "briefing.pdf" in prompt
    assert "120 m²" in prompt
    assert "Não invente conteúdo" in prompt


def test_runtime_hints_expose_metadata_not_document_contents():
    hints = merge_glip_aria_document_runtime_hints(
        {"routing": {"route_applied": True}},
        {
            "context_available": True,
            "context_chars": 420,
            "file_ids": ["f1"],
            "files_used": ["briefing.pdf"],
            "file_context_block": "SEGREDO DO DOCUMENTO",
        },
    )
    assert hints["glip_documents"]["context_available"] is True
    assert hints["glip_documents"]["context_chars"] == 420
    assert hints["glip_documents"]["files_used"] == ["briefing.pdf"]
    assert "SEGREDO DO DOCUMENTO" not in str(hints)


def test_terminal_event_preserves_aria_identity_and_artifact():
    artifact = {
        "file_id": "file-1",
        "filename": "proposta.pdf",
        "download_url": "/api/files/file-1/download",
    }
    events = build_glip_aria_terminal_events(
        {"thread_id": "thread-1", "trace_id": "trace-1"},
        {
            "thread_id": "thread-1",
            "assistant_persisted": True,
            "assistant_message_id": "message-1",
            "artifact": artifact,
            "artifacts": [artifact],
        },
        final_text="Aria criou o arquivo.",
        runtime_hints={"routing": {"route_applied": True}},
    )

    done = [payload for event, payload in events if event == "done"][0]
    assert done["agent_id"] == "aria"
    assert done["agent_name"] == "Aria"
    assert done["final_speaker"] == "Aria"
    assert done["artifact_created"] is True
    assert done["artifact"]["filename"] == "proposta.pdf"
    assert done["assistant_message_id"] == "message-1"


def test_main_has_thin_glip_document_wiring_and_no_inline_source_plan_relaxation():
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    bridge_source = (
        ROOT / "runtime" / "glip_aria_document_bridge.py"
    ).read_text(encoding="utf-8")

    assert "execute_glip_aria_document_stream(" in source
    assert "load_glip_aria_document_context(" in source
    assert '"aria": "Aria"' in source
    assert "GlipAriaDocumentArtifactGenerateIn.model_validate(input_payload)" in source
    assert "class GlipAriaDocumentArtifactGenerateIn" in bridge_source
    assert "class DocumentArtifactGenerateIn" not in source
