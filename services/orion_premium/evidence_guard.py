from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


DOCUMENT_EVIDENCE_FALLBACK_PT_BR = (
    "Recebi o documento, mas não consegui confirmar que o conteúdo foi "
    "extraído e disponibilizado para análise. Para evitar conclusões sem "
    "evidência, não vou inferir o conteúdo apenas pelo nome do arquivo."
)


@dataclass(frozen=True)
class DocumentGroundingDecision:
    allowed: bool
    mode: str
    reason: str
    file_count: int
    evidence_count: int
    context_chars: int
    files_used: tuple[str, ...]
    grounding_score: float

    def as_runtime_hint(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "mode": self.mode,
            "reason": self.reason,
            "file_count": self.file_count,
            "evidence_count": self.evidence_count,
            "context_chars": self.context_chars,
            "files_used": list(self.files_used),
            "grounding_score": self.grounding_score,
        }


def _safe_non_negative_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _normalize_files_used(value: Any) -> tuple[str, ...]:
    if not isinstance(value, Iterable) or isinstance(value, (str, bytes, Mapping)):
        return ()

    normalized: list[str] = []
    for item in value:
        if isinstance(item, Mapping):
            candidate = (
                item.get("filename")
                or item.get("file_id")
                or item.get("id")
                or item.get("source_id")
            )
        else:
            candidate = item

        text = str(candidate or "").strip()
        if text and text not in normalized:
            normalized.append(text)

    return tuple(normalized)


def evaluate_document_grounding(
    document_context: Mapping[str, Any] | None,
) -> DocumentGroundingDecision:
    """Evaluate existing ORKIO document-context output without changing retrieval.

    Fail closed whenever a file exists but no extracted evidence/context is proven.
    This function is deterministic and has no database, model or network side effects.
    """
    context = dict(document_context or {})
    file_ids = [
        str(item).strip()
        for item in list(context.get("file_ids") or [])
        if str(item).strip()
    ]
    evidence_count = _safe_non_negative_int(context.get("file_evidence_count"))
    context_chars = _safe_non_negative_int(context.get("file_context_chars"))
    citations = list(context.get("citations") or [])
    files_used = _normalize_files_used(context.get("files_used") or [])

    # Existing service may express proof through citations even if the aggregate
    # counter is absent. Never infer proof from filename/file-id alone.
    citation_count = len(
        [item for item in citations if isinstance(item, Mapping)]
    )
    effective_evidence = max(evidence_count, citation_count)
    injected = bool(context.get("file_context_injected"))
    has_proven_context = bool(
        injected and effective_evidence > 0 and context_chars > 0
    )

    if not file_ids:
        return DocumentGroundingDecision(
            allowed=False,
            mode="no_document_attached",
            reason="no_thread_scoped_file",
            file_count=0,
            evidence_count=0,
            context_chars=0,
            files_used=(),
            grounding_score=0.0,
        )

    if not has_proven_context:
        return DocumentGroundingDecision(
            allowed=False,
            mode="document_hypothesis_only",
            reason="document_extraction_not_proven",
            file_count=len(file_ids),
            evidence_count=effective_evidence,
            context_chars=context_chars,
            files_used=files_used,
            grounding_score=0.0,
        )

    # Conservative score: evidence breadth and context volume both matter.
    breadth = min(1.0, effective_evidence / 4.0)
    volume = min(1.0, context_chars / 4000.0)
    score = round((breadth * 0.6) + (volume * 0.4), 3)

    return DocumentGroundingDecision(
        allowed=True,
        mode="document_evidence_based",
        reason="document_extraction_proven",
        file_count=len(file_ids),
        evidence_count=effective_evidence,
        context_chars=context_chars,
        files_used=files_used,
        grounding_score=score,
    )


def build_fail_closed_overlay(
    decision: DocumentGroundingDecision,
) -> str:
    """Build a deterministic fail-closed overlay for document requests.

    No overlay is added when no document is attached or when extraction evidence
    has already been proven. When a document exists without proven extraction,
    the returned text instructs the runtime not to infer document content.
    """
    if decision.mode == "no_document_attached":
        return ""

    if decision.allowed:
        return ""

    return (
        "[ORION EVIDENCE GUARD — FAIL CLOSED]\n"
        "Existe documento associado à conversa, mas o conteúdo extraído "
        "não foi comprovado pelo contexto disponível.\n"
        "Não afirme, resuma, compare, classifique ou conclua nada sobre o "
        "conteúdo do documento com base apenas no nome do arquivo, metadados "
        "ou suposições.\n"
        f"Motivo técnico: {decision.reason}.\n"
        f"Orientação obrigatória ao usuário: "
        f"{DOCUMENT_EVIDENCE_FALLBACK_PT_BR}"
    )


def evaluate_media_grounding(
    *,
    mime_type: str,
    vision_evidence: dict | None = None,
) -> DocumentGroundingDecision:
    """Fail closed for image attachments unless real visual evidence exists."""
    mime = str(mime_type or "").strip().lower()

    if not mime.startswith("image/"):
        return DocumentGroundingDecision(
            allowed=True,
            mode="not_image",
            reason="media_guard_not_applicable",
            file_count=0,
            evidence_count=0,
            context_chars=0,
            files_used=(),
            grounding_score=1.0,
        )

    evidence = dict(vision_evidence or {})
    processed = bool(evidence.get("processed"))
    description = str(evidence.get("description") or "").strip()
    allowed = processed and bool(description)

    return DocumentGroundingDecision(
        allowed=allowed,
        mode="image_vision_evidence" if allowed else "image_vision_unavailable",
        reason="vision_processed" if allowed else "vision_evidence_missing",
        file_count=1,
        evidence_count=1 if allowed else 0,
        context_chars=len(description),
        files_used=(),
        grounding_score=1.0 if allowed else 0.0,
    )
