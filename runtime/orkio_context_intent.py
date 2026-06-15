from __future__ import annotations

"""
AO75A — Orkio Context Intent Contract

Pure, dependency-free intent classification shared by the public gateway,
Decision Mesh, public Orkio policy and the main chat runtime.

The module does not read the database, call providers, persist memory or expose
internal agents. It only returns a bounded routing contract.
"""

import re
import unicodedata
from typing import Any, Dict, Iterable, List, Optional

ORKIO_CONTEXT_INTENT_VERSION = "AO75A_HF1_CONTEXT_INTENT_V1"
PUBLIC_SPEAKER = "Orkio"

_DOCUMENT_FILE_PATTERN = re.compile(
    r"(?<![\w/.-])[\w .()\-]{1,160}\.(?:pdf|docx?|pptx?|xlsx?|csv|txt|md|rtf|odt)(?![\w/.-])",
    flags=re.IGNORECASE,
)


def normalize_context_text(value: Any) -> str:
    raw = str(value or "")
    try:
        raw = unicodedata.normalize("NFD", raw)
        raw = "".join(ch for ch in raw if unicodedata.category(ch) != "Mn")
    except Exception:
        pass
    raw = raw.lower()
    raw = re.sub(r"[^a-z0-9@:/.\-_\s?]+", " ", raw, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", raw).strip()


def _message_text(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("content", "message", "text", "final_text", "answer"):
            text = str(value.get(key) or "").strip()
            if text:
                return text
        return ""
    for key in ("content", "message", "text", "final_text", "answer"):
        try:
            text = str(getattr(value, key, "") or "").strip()
        except Exception:
            text = ""
        if text:
            return text
    return str(value or "").strip()


def _recent_context(previous_messages: Optional[Iterable[Any]], limit: int = 8) -> List[str]:
    out: List[str] = []
    for item in list(previous_messages or [])[-max(1, int(limit or 8)):]:
        text = _message_text(item)
        if text:
            out.append(text)
    return out


def _contains_any(text: str, markers: Iterable[str]) -> bool:
    return any(marker in text for marker in markers)


def _matched(text: str, markers: Iterable[str]) -> List[str]:
    return [marker for marker in markers if marker in text][:8]


def _contract(
    *,
    intent: str,
    reason: str,
    confidence: float,
    explicit: bool,
    requires_document_context: bool = False,
    public_fastpath_allowed: bool = True,
    memory_commit_allowed: bool = False,
    matched_markers: Optional[List[str]] = None,
    continuation: bool = False,
) -> Dict[str, Any]:
    concrete_intents = {
        "document_analysis",
        "document_summary",
        "document_comparison",
        "document_status",
        "document_reference",
        "document_creation",
        "technical_diagnostic",
        "code_audit",
        "business_plan",
        "project_strategy",
        "product_design",
    }
    return {
        "version": ORKIO_CONTEXT_INTENT_VERSION,
        "intent": intent,
        "reason": reason,
        "confidence": round(max(0.0, min(1.0, float(confidence))), 3),
        "explicit": bool(explicit),
        "requires_document_context": bool(requires_document_context),
        "public_fastpath_allowed": bool(public_fastpath_allowed),
        "memory_commit_allowed": bool(memory_commit_allowed),
        "concrete_task": intent in concrete_intents,
        "continuation": bool(continuation),
        "speaker": PUBLIC_SPEAKER,
        "matched_markers": list(matched_markers or [])[:8],
    }


def classify_orkio_context_intent(
    message: Any,
    *,
    previous_messages: Optional[Iterable[Any]] = None,
    has_thread_files: bool = False,
) -> Dict[str, Any]:
    raw = str(message or "").strip()
    text = normalize_context_text(raw)
    recent_raw = _recent_context(previous_messages)
    recent = normalize_context_text(" ".join(recent_raw))

    if not text:
        return _contract(
            intent="unknown",
            reason="empty_message",
            confidence=0.0,
            explicit=False,
            public_fastpath_allowed=True,
        )

    direct_answer_markers = (
        "responda apenas",
        "responda somente",
        "diga exatamente",
        "retorne somente",
        "answer only",
        "reply only",
    )
    if _contains_any(text, direct_answer_markers):
        return _contract(
            intent="general_conversation",
            reason="direct_answer_constraint",
            confidence=0.99,
            explicit=True,
            public_fastpath_allowed=True,
            matched_markers=_matched(text, direct_answer_markers),
        )

    filename_present = bool(_DOCUMENT_FILE_PATTERN.search(raw))
    strong_document_nouns = (
        "anexo",
        "anexado",
        "anexada",
        "arquivo",
        "documento",
        "docx",
        "pdf",
        "pptx",
        "planilha",
        "upload",
    )
    soft_document_nouns = (
        "regulamento",
        "apresentacao",
        "material",
    )
    document_nouns = strong_document_nouns + soft_document_nouns
    sent_markers = (
        "mandei",
        "enviei",
        "enviado",
        "enviada",
        "mandado",
        "mandada",
        "encaminhei",
        "anexei",
        "subi",
        "carreguei",
        "fiz o upload",
        "acabei de enviar",
        "acabei de mandar",
        "uploaded",
        "attached",
        "sent you",
    )
    sent_objects = (
        "projeto",
        "material",
        "arquivo",
        "documento",
        "apresentacao",
        "regulamento",
        "proposta",
        "plano",
        "versao",
    )
    analysis_markers = (
        "analis",
        "avalie",
        "avaliar",
        "revis",
        "leia",
        "ler ",
        "dar uma olhada",
        "de uma olhada",
        "explique o conteudo",
        "o que diz",
        "what does",
        "analyze",
        "analyse",
        "review",
        "read the",
    )
    summary_markers = (
        "resum",
        "sintet",
        "sumar",
        "conteudo",
        "pontos principais",
        "principais pontos",
        "executive summary",
        "summary",
        "summarize",
        "summarise",
        "what is in",
    )
    comparison_markers = (
        "compare",
        "comparar",
        "comparacao",
        "diferenca",
        "diferencas",
        "versao anterior",
        "arquivo anterior",
        "documento anterior",
        "os dois",
        "ambos",
        "compare with",
        "previous version",
    )
    status_markers = (
        "chegou",
        "recebeu",
        "foi recebido",
        "esta disponivel",
        "esta pronto",
        "processando",
        "conseguiu acessar",
        "consegue acessar",
        "arquivo chegou",
        "documento chegou",
        "did you receive",
        "is the file",
    )
    deictic_markers = (
        "esse arquivo",
        "este arquivo",
        "o arquivo",
        "esse documento",
        "este documento",
        "o documento",
        "o anexo",
        "esse anexo",
        "o projeto enviado",
        "projeto que enviei",
        "projeto que mandei",
        "que te mandei",
        "que eu mandei",
        "que te enviei",
        "que eu enviei",
        "que anexei",
        "em anexo",
        "aqui anexado",
        "aqui em anexo",
        "the file",
        "the document",
        "the attachment",
        "the project sent",
    )
    continuity_markers = (
        "continue de onde paramos",
        "continue de onde parou",
        "continue a analise",
        "continue a leitura",
        "faca a mesma analise",
        "prossiga com a analise",
        "retome a analise",
        "continue from where",
        "continue the analysis",
    )
    creation_markers = (
        "crie",
        "criar",
        "gere",
        "gerar",
        "monte",
        "montar",
        "prepare",
        "preparar",
        "escreva",
        "redija",
        "faca uma",
        "faça uma",
        "create",
        "generate",
        "write",
        "prepare",
    )

    has_strong_document_noun = _contains_any(text, strong_document_nouns)
    has_soft_document_noun = _contains_any(text, soft_document_nouns)
    has_sent_reference = _contains_any(text, sent_markers) and _contains_any(text, sent_objects)
    has_deictic_reference = _contains_any(text, deictic_markers)
    has_analysis_action = _contains_any(text, analysis_markers)
    has_summary_action = _contains_any(text, summary_markers)
    has_comparison_action = _contains_any(text, comparison_markers)
    has_status_action = _contains_any(text, status_markers)
    has_continuity = _contains_any(text, continuity_markers)
    has_creation_action = _contains_any(text, creation_markers)

    if (
        has_creation_action
        and (has_strong_document_noun or has_soft_document_noun or filename_present)
        and not has_sent_reference
        and not has_deictic_reference
        and not has_analysis_action
        and not has_summary_action
        and not has_comparison_action
        and not has_status_action
    ):
        return _contract(
            intent="document_creation",
            reason="document_creation_task",
            confidence=0.95,
            explicit=True,
            requires_document_context=False,
            public_fastpath_allowed=False,
            memory_commit_allowed=False,
            matched_markers=(
                _matched(text, creation_markers)
                + _matched(text, document_nouns)
            ),
        )

    previous_was_documental = _contains_any(
        recent,
        tuple(document_nouns) + tuple(sent_markers) + tuple(deictic_markers),
    )

    document_reference = bool(
        filename_present
        or has_strong_document_noun
        or has_sent_reference
        or (
            has_soft_document_noun
            and (
                has_analysis_action
                or has_summary_action
                or has_comparison_action
                or has_status_action
                or has_deictic_reference
                or has_thread_files
            )
        )
        or (has_thread_files and has_deictic_reference)
        or (has_thread_files and has_comparison_action)
        or (has_thread_files and has_continuity and previous_was_documental)
    )

    if document_reference:
        markers = []
        markers.extend(_matched(text, document_nouns))
        markers.extend(_matched(text, sent_markers))
        markers.extend(_matched(text, deictic_markers))
        markers = list(dict.fromkeys(markers))[:8]

        if has_comparison_action:
            return _contract(
                intent="document_comparison",
                reason="document_comparison_request",
                confidence=0.99 if filename_present or has_thread_files else 0.91,
                explicit=True,
                requires_document_context=True,
                public_fastpath_allowed=False,
                memory_commit_allowed=False,
                matched_markers=markers + _matched(text, comparison_markers),
                continuation=has_continuity,
            )
        if has_status_action and not (has_analysis_action or has_summary_action):
            return _contract(
                intent="document_status",
                reason="document_status_request",
                confidence=0.98,
                explicit=True,
                requires_document_context=True,
                public_fastpath_allowed=False,
                memory_commit_allowed=False,
                matched_markers=markers + _matched(text, status_markers),
                continuation=has_continuity,
            )
        if has_summary_action:
            return _contract(
                intent="document_summary",
                reason="document_summary_request",
                confidence=0.99 if filename_present or has_thread_files else 0.93,
                explicit=True,
                requires_document_context=True,
                public_fastpath_allowed=False,
                memory_commit_allowed=False,
                matched_markers=markers + _matched(text, summary_markers),
                continuation=has_continuity,
            )
        if has_analysis_action or has_continuity:
            return _contract(
                intent="document_analysis",
                reason="document_analysis_request",
                confidence=0.99 if filename_present or has_thread_files else 0.93,
                explicit=True,
                requires_document_context=True,
                public_fastpath_allowed=False,
                memory_commit_allowed=False,
                matched_markers=markers + _matched(text, analysis_markers),
                continuation=has_continuity,
            )
        return _contract(
            intent="document_reference",
            reason="document_reference_requires_context",
            confidence=0.96 if has_sent_reference or filename_present else 0.88,
            explicit=bool(has_sent_reference or filename_present or has_deictic_reference),
            requires_document_context=True,
            public_fastpath_allowed=False,
            memory_commit_allowed=False,
            matched_markers=markers,
            continuation=has_continuity,
        )

    technical_markers = (
        "falha",
        "logs",
        "log ",
        "traceback",
        "stacktrace",
        "runtime",
        "backend",
        "frontend",
        "endpoint",
        "deploy",
        "build",
        "github",
        "codigo",
        "patch",
        "auditoria",
        "diagnostico tecnico",
        "causa raiz",
        "fastapi",
        "react",
        "webrtc",
    )
    audit_markers = (
        "audite",
        "auditar",
        "auditoria",
        "revise o codigo",
        "analise o codigo",
        "code audit",
        "review the code",
    )
    if _contains_any(text, audit_markers):
        return _contract(
            intent="code_audit",
            reason="explicit_code_audit",
            confidence=0.97,
            explicit=True,
            public_fastpath_allowed=False,
            memory_commit_allowed=False,
            matched_markers=_matched(text, audit_markers),
        )
    technical_short_token = bool(
        re.search(r"\b(?:erro|bug|api|sse|code)\b", text)
    )
    if _contains_any(text, technical_markers) or technical_short_token:
        return _contract(
            intent="technical_diagnostic",
            reason="explicit_technical_task",
            confidence=0.9,
            explicit=True,
            public_fastpath_allowed=False,
            memory_commit_allowed=False,
            matched_markers=_matched(text, technical_markers),
        )

    contact_markers = (
        "falar com a equipe",
        "falar com alguem",
        "contato",
        "whatsapp",
        "atendimento humano",
        "talk to the team",
        "human support",
        "contact the team",
    )
    if _contains_any(text, contact_markers):
        return _contract(
            intent="contact_request",
            reason="explicit_contact_request",
            confidence=0.98,
            explicit=True,
            public_fastpath_allowed=True,
            memory_commit_allowed=False,
            matched_markers=_matched(text, contact_markers),
        )

    navigation_markers = (
        "site oficial",
        "qual e o site",
        "link oficial",
        "patroai.com",
        "official website",
        "website",
    )
    if _contains_any(text, navigation_markers):
        return _contract(
            intent="navigation",
            reason="official_navigation_request",
            confidence=0.97,
            explicit=True,
            public_fastpath_allowed=True,
            memory_commit_allowed=False,
            matched_markers=_matched(text, navigation_markers),
        )

    realtime_markers = (
        "realtime",
        "tempo real",
        "sessao de voz",
        "conversa por voz",
        "falar por voz",
        "voice session",
        "real time voice",
    )
    if _contains_any(text, realtime_markers):
        return _contract(
            intent="realtime_request",
            reason="realtime_conversation_request",
            confidence=0.94,
            explicit=True,
            public_fastpath_allowed=True,
            memory_commit_allowed=False,
            matched_markers=_matched(text, realtime_markers),
        )

    institutional_markers = (
        "o que e a patroai",
        "quem e a patroai",
        "what is patroai",
        "who is patroai",
        "o que e o orkio",
        "quem e o orkio",
        "como funciona o orkio",
        "what is orkio",
        "who is orkio",
        "how does orkio work",
        "o que e factoryai",
        "factoryai",
        "factory ai",
        "o que e console tech",
        "console tech",
        "amcham",
        "membro da amcham",
    )
    if _contains_any(text, institutional_markers):
        return _contract(
            intent="institutional_question",
            reason="canonical_institutional_question",
            confidence=0.98,
            explicit=True,
            public_fastpath_allowed=True,
            memory_commit_allowed=False,
            matched_markers=_matched(text, institutional_markers),
        )

    business_plan_markers = (
        "business plan",
        "plano de negocios",
        "plano de negocio",
        "modelo de negocio",
        "projecoes financeiras",
        "valuation",
    )
    if _contains_any(text, business_plan_markers):
        return _contract(
            intent="business_plan",
            reason="business_plan_task",
            confidence=0.95,
            explicit=True,
            public_fastpath_allowed=False,
            memory_commit_allowed=False,
            matched_markers=_matched(text, business_plan_markers),
        )

    product_design_markers = (
        "desenhar o produto",
        "design de produto",
        "roadmap de produto",
        "mvp",
        "arquitetura do produto",
        "product design",
        "product roadmap",
    )
    if _contains_any(text, product_design_markers):
        return _contract(
            intent="product_design",
            reason="product_design_task",
            confidence=0.92,
            explicit=True,
            public_fastpath_allowed=False,
            memory_commit_allowed=False,
            matched_markers=_matched(text, product_design_markers),
        )

    project_markers = (
        "criar um projeto",
        "novo projeto",
        "estruturar o projeto",
        "estrategia do projeto",
        "plano do projeto",
        "projeto da",
        "project strategy",
        "create a project",
    )
    if _contains_any(text, project_markers):
        return _contract(
            intent="project_strategy",
            reason="project_strategy_task",
            confidence=0.9,
            explicit=True,
            public_fastpath_allowed=False,
            memory_commit_allowed=False,
            matched_markers=_matched(text, project_markers),
        )

    return _contract(
        intent="general_conversation",
        reason="no_specialized_intent",
        confidence=0.55,
        explicit=False,
        public_fastpath_allowed=True,
        memory_commit_allowed=False,
    )


def public_fastpath_allowed(intent_contract: Optional[Dict[str, Any]]) -> bool:
    if not isinstance(intent_contract, dict):
        return True
    return bool(intent_contract.get("public_fastpath_allowed", True))


def requires_document_context(intent_contract: Optional[Dict[str, Any]]) -> bool:
    if not isinstance(intent_contract, dict):
        return False
    return bool(intent_contract.get("requires_document_context", False))


def is_concrete_user_task(intent_contract: Optional[Dict[str, Any]]) -> bool:
    if not isinstance(intent_contract, dict):
        return False
    return bool(intent_contract.get("concrete_task", False))
