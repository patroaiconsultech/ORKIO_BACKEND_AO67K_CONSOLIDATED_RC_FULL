from __future__ import annotations

import base64
import json
import logging
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


@dataclass(frozen=True)
class VisionEvidence:
    processed: bool
    mode: str
    reason: str
    mime_type: str
    model: Optional[str] = None
    description: str = ""
    extracted_text: str = ""
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def is_supported_image(filename: str, mime_type: Optional[str]) -> bool:
    mime = str(mime_type or "").strip().lower()
    name = str(filename or "").strip().lower()
    return mime in SUPPORTED_IMAGE_MIME_TYPES or name.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif"))


def _enabled(name: str, default: bool) -> bool:
    raw = str(os.getenv(name, "true" if default else "false") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def analyze_image(
    *,
    filename: str,
    raw: bytes,
    mime_type: Optional[str],
    prompt: Optional[str] = None,
) -> VisionEvidence:
    mime = str(mime_type or "").strip().lower() or "application/octet-stream"
    if not is_supported_image(filename, mime):
        return VisionEvidence(False, "not_image", "unsupported_media_type", mime)

    if not _enabled("ORKIO_VISION_PIPELINE_ENABLED", False):
        return VisionEvidence(False, "image_vision_unavailable", "vision_pipeline_disabled", mime)

    api_key = str(os.getenv("OPENAI_API_KEY", "") or "").strip()
    if not api_key:
        return VisionEvidence(False, "image_vision_unavailable", "openai_api_key_missing", mime)

    try:
        from openai import OpenAI
    except Exception:
        logger.exception("ORION_VISION_OPENAI_IMPORT_FAILED")
        return VisionEvidence(False, "image_vision_unavailable", "openai_client_unavailable", mime)

    model = str(os.getenv("OPENAI_VISION_MODEL", "") or os.getenv("OPENAI_MODEL", "") or "gpt-4o-mini").strip()
    timeout_s = float(os.getenv("OPENAI_VISION_TIMEOUT", "45") or "45")
    encoded = base64.b64encode(raw or b"").decode("ascii")
    data_url = f"data:{mime};base64,{encoded}"
    user_prompt = str(prompt or "").strip() or (
        "Analise esta imagem como evidência. Descreva apenas o que é visualmente verificável, "
        "transcreva texto legível, se houver, separe observação de inferência e não identifique "
        "pessoas sem evidência contextual fornecida pelo usuário."
    )

    try:
        client = OpenAI(api_key=api_key, timeout=timeout_s)
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Você é o gateway visual da ORKIO. Produza JSON válido com as chaves "
                        "description, extracted_text, confidence. Não invente detalhes."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            response_format={"type": "json_object"},
        )
        content = ((response.choices or [])[0].message.content or "").strip()
        payload = json.loads(content or "{}")
        description = str(payload.get("description") or "").strip()
        extracted_text = str(payload.get("extracted_text") or "").strip()
        try:
            confidence = max(0.0, min(float(payload.get("confidence") or 0.0), 1.0))
        except Exception:
            confidence = 0.0
        evidence_text = "\n\n".join(part for part in (
            f"[EVIDÊNCIA VISUAL: {filename}]",
            f"Descrição verificável: {description}" if description else "",
            f"Texto visível: {extracted_text}" if extracted_text else "",
            f"Confiança declarada: {confidence:.2f}",
        ) if part)
        if not description and not extracted_text:
            return VisionEvidence(False, "image_vision_empty", "vision_returned_no_evidence", mime, model=model)
        return VisionEvidence(
            True,
            "image_vision_evidence",
            "vision_processed",
            mime,
            model=model,
            description=evidence_text,
            extracted_text=extracted_text,
            confidence=confidence,
        )
    except Exception as exc:
        logger.exception("ORION_VISION_PROCESSING_FAILED filename=%s mime=%s", filename, mime)
        return VisionEvidence(False, "image_vision_error", exc.__class__.__name__, mime, model=model)
