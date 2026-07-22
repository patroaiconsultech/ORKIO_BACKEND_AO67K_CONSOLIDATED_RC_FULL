from __future__ import annotations

import asyncio

from typing import Any, Dict, List, Optional, Tuple

from pydantic import Field
from sqlalchemy.orm import Session

from ..runtime.document_artifact_intent import (
    build_document_artifact_payload,
    classify_document_artifact_request,
    has_document_artifact_write_blocker,
)
from ..schemas.document_artifacts import DocumentArtifactGenerateIn
from ..services.document_context_service import build_thread_document_context


GLIP_ARIA_DOCUMENT_BRIDGE_VERSION = "AO-GLIP11A"
GLIP_ARIA_READ_FORMATS = ("pdf", "docx", "xlsx", "pptx", "csv", "txt", "md")
GLIP_ARIA_CREATE_FORMATS = ("pdf", "docx", "xlsx", "pptx", "csv", "md")


class GlipAriaDocumentArtifactGenerateIn(DocumentArtifactGenerateIn):
    """Trusted GLIP-only execution contract.

    The public DOCIO schema remains strict. GLIP's internal conversational bridge
    may carry the bounded ``source_plan`` produced by the backend planner so PPTX
    coverage metadata reaches the isolated generator without accepting arbitrary
    client-supplied fields.
    """

    source_plan: Optional[Dict[str, Any]] = Field(default=None)


def classify_glip_aria_document_request(message: Any) -> Dict[str, Any]:
    if has_document_artifact_write_blocker(message):
        return {
            "handled": False,
            "reason": "governance_write_blocked",
            "agent_slug": "aria",
        }

    decision = dict(
        classify_document_artifact_request(
            message,
            # The common DOCIO classifier currently permits Orkio/Orion only.
            # GLIP performs its own locked-owner authorization and rewrites the
            # resulting execution owner to Aria below.
            agent_slug="orkio",
        )
        or {}
    )
    if decision.get("handled"):
        decision["agent_slug"] = "aria"
        decision["resolved_agent"] = "Aria"
        decision["bridge_version"] = GLIP_ARIA_DOCUMENT_BRIDGE_VERSION
    return decision


def build_glip_aria_artifact_input(
    message: Any,
    decision: Dict[str, Any],
    *,
    thread_id: Optional[str],
    source_context: Any = None,
) -> GlipAriaDocumentArtifactGenerateIn:
    payload = build_document_artifact_payload(
        message,
        decision,
        thread_id=thread_id,
        requested_agent_hint="aria",
        source_context=source_context,
    )
    return GlipAriaDocumentArtifactGenerateIn.model_validate(payload)


def load_glip_aria_document_context(
    db: Session,
    *,
    org: str,
    thread_id: Optional[str],
    query: Any,
    top_k: int = 8,
) -> Dict[str, Any]:
    tid = str(thread_id or "").strip()
    if not tid:
        return {
            "ok": True,
            "thread_id": None,
            "context_available": False,
            "context_block": "",
            "file_context_block": "",
            "citations": [],
            "files_used": [],
            "context_chars": 0,
            "bridge_version": GLIP_ARIA_DOCUMENT_BRIDGE_VERSION,
        }

    context = dict(
        build_thread_document_context(
            db,
            org=str(org or "").strip(),
            thread_id=tid,
            query=str(query or ""),
            top_k=max(1, min(int(top_k or 8), 12)),
        )
        or {}
    )
    context["bridge_version"] = GLIP_ARIA_DOCUMENT_BRIDGE_VERSION
    return context


def build_glip_aria_document_system_prompt(
    base_prompt: Any,
    context: Any,
) -> str:
    prompt = str(base_prompt or "").strip()
    context_map = context if isinstance(context, dict) else {}
    context_block = str(
        context_map.get("file_context_block")
        or context_map.get("context_block")
        or ""
    ).strip()
    if not context_block:
        return prompt

    document_instruction = (
        "MODO DOCUMENTAL GLIP — LEITURA AUTORIZADA DA THREAD.\n"
        "Use somente as evidências presentes no bloco documental abaixo. "
        "Diferencie claramente fatos extraídos, inferências e dados ausentes. "
        "Não invente conteúdo, não diga que o arquivo está inacessível quando "
        "houver evidência disponível e preserve a identidade visível da Aria.\n\n"
        f"{context_block}"
    )
    return f"{prompt}\n\n{document_instruction}".strip()


def glip_aria_document_citations(context: Any) -> List[Dict[str, Any]]:
    context_map = context if isinstance(context, dict) else {}
    citations = context_map.get("citations")
    return [dict(item) for item in list(citations or []) if isinstance(item, dict)]


def merge_glip_aria_document_runtime_hints(
    base_hints: Any,
    context: Any,
) -> Dict[str, Any]:
    hints = dict(base_hints or {}) if isinstance(base_hints, dict) else {}
    context_map = context if isinstance(context, dict) else {}
    hints["glip_documents"] = {
        "bridge_version": GLIP_ARIA_DOCUMENT_BRIDGE_VERSION,
        "context_available": bool(context_map.get("context_available")),
        "context_chars": int(context_map.get("context_chars") or 0),
        "file_count": len(list(context_map.get("file_ids") or [])),
        "files_used": list(context_map.get("files_used") or [])[:8],
        "read_formats": list(GLIP_ARIA_READ_FORMATS),
        "create_formats": list(GLIP_ARIA_CREATE_FORMATS),
    }
    return hints


def build_glip_aria_document_start_events(
    base: Dict[str, Any],
    decision: Dict[str, Any],
) -> List[Tuple[str, Dict[str, Any]]]:
    event_base = {
        **dict(base or {}),
        "agent_id": "aria",
        "agent_name": "Aria",
        "final_speaker": "Aria",
    }
    fmt = str(decision.get("format") or "arquivo").strip().lower()
    return [
        (
            "status",
            {
                **event_base,
                "status": "Aria está criando o arquivo solicitado.",
                "phase": "glip_document_artifact_generation",
                "capability": "document_artifact_generate",
                "format": fmt,
            },
        ),
        (
            "execution",
            {
                **event_base,
                "step": "document_artifact_generate",
                "kind": "tool",
                "label": "Criar arquivo",
                "message": "Aria está estruturando e registrando o documento.",
                "detail": f"Execução documental GLIP ({fmt}).",
            },
        ),
    ]


def build_glip_aria_terminal_events(
    base: Dict[str, Any],
    payload: Any,
    *,
    final_text: str,
    runtime_hints: Optional[Dict[str, Any]] = None,
) -> List[Tuple[str, Dict[str, Any]]]:
    data = dict(payload or {}) if isinstance(payload, dict) else {}
    event_base = {
        **dict(base or {}),
        "thread_id": str(data.get("thread_id") or base.get("thread_id") or "").strip() or None,
        "agent_id": "aria",
        "agent_name": "Aria",
        "final_speaker": "Aria",
        "assistant_message_id": data.get("assistant_message_id"),
        "message_id": data.get("assistant_message_id"),
        "assistant_persisted": bool(data.get("assistant_persisted", True)),
    }
    text = str(final_text or "").strip()
    hints = dict(runtime_hints or {}) if isinstance(runtime_hints, dict) else {}
    artifact = data.get("artifact")
    artifacts = list(data.get("artifacts") or [])
    if artifact and not artifacts:
        artifacts = [artifact]

    return [
        (
            "status",
            {
                **event_base,
                "status": "Resposta preparada.",
                "phase": "answer_ready",
            },
        ),
        (
            "chunk",
            {
                **event_base,
                "delta": text,
                "content": text,
            },
        ),
        (
            "agent_done",
            {
                **event_base,
                "done": True,
                "message": "Resposta concluída.",
            },
        ),
        (
            "done",
            {
                **event_base,
                "done": True,
                "final_text": text,
                "citations": data.get("citations") or [],
                "artifact": artifact,
                "artifacts": artifacts,
                "artifact_created": bool(artifact or artifacts),
                "voice_id": data.get("voice_id") or "marin",
                "avatar_url": data.get("avatar_url"),
                "runtime_hints": hints,
            },
        ),
    ]


def build_glip_aria_document_error_events(
    base: Dict[str, Any],
    *,
    error_type: Optional[str] = None,
) -> List[Tuple[str, Dict[str, Any]]]:
    event_base = {
        **dict(base or {}),
        "agent_id": "aria",
        "agent_name": "Aria",
        "final_speaker": "Aria",
    }
    safe_error = (
        "Não foi possível criar o arquivo nesta execução. "
        "A tentativa foi encerrada com segurança; revise o pedido e tente novamente."
    )
    return [
        (
            "error",
            {
                **event_base,
                "error": safe_error,
                "message": safe_error,
                "code": "GLIP_DOCUMENT_ARTIFACT_GENERATION_FAILED",
                "capability": "document_artifact_generate",
            },
        ),
        (
            "done",
            {
                **event_base,
                "done": True,
                "assistant_persisted": False,
                "assistant_message_id": None,
                "final_text": safe_error,
                "artifact": None,
                "artifacts": [],
                "artifact_created": False,
                "runtime_hints": {
                    "routing": {
                        "routing_source": "glip_aria_document_bridge",
                        "execution_lifecycle": "failed",
                        "route_applied": True,
                    },
                    "glip_documents": {
                        "bridge_version": GLIP_ARIA_DOCUMENT_BRIDGE_VERSION,
                        "write_executed": False,
                        "error_type": str(error_type or "DocumentArtifactError"),
                    },
                },
            },
        ),
    ]

async def execute_glip_aria_document_stream(
    *,
    message: Any,
    base: Dict[str, Any],
    runner: Any,
    safe_payload: Any,
    sanitize_visible_text: Any,
    clean_answer: Any,
    fallback_message: str,
    logger: Any = None,
    trace_id: Optional[str] = None,
    thread_id: Optional[str] = None,
) -> Optional[List[Tuple[str, Dict[str, Any]]]]:
    """Execute the GLIP document write rail outside ``main.py``.

    ``None`` means the message is not an explicit document creation request.
    A returned event list is always terminal: success ends in ``done`` and
    failures end in ``error`` followed by ``done``.
    """

    decision = classify_glip_aria_document_request(message)
    if not bool(decision.get("handled")):
        return None

    events = build_glip_aria_document_start_events(base, decision)
    try:
        payload = await asyncio.to_thread(runner, decision)
        payload = safe_payload(payload)
        if not isinstance(payload, dict):
            payload = {}

        final_text = str(
            payload.get("answer")
            or payload.get("message")
            or payload.get("final_text")
            or payload.get("content")
            or ""
        ).strip()
        final_text = clean_answer(
            sanitize_visible_text(final_text),
            fallback_message=fallback_message,
        )
        runtime_hints = (
            payload.get("runtime_hints")
            if isinstance(payload.get("runtime_hints"), dict)
            else {}
        )
        events.extend(
            build_glip_aria_terminal_events(
                base,
                payload,
                final_text=final_text,
                runtime_hints=runtime_hints,
            )
        )
    except Exception as exc:
        if logger is not None:
            try:
                logger.exception(
                    "AO_GLIP11_ARIA_DOCUMENT_GENERATION_FAILED trace_id=%s thread_id=%s",
                    trace_id,
                    thread_id,
                )
            except Exception:
                pass
        events.extend(
            build_glip_aria_document_error_events(
                base,
                error_type=exc.__class__.__name__,
            )
        )
    return events

