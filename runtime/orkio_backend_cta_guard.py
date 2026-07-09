from __future__ import annotations

"""Backend-side commercial CTA suppression guard for MANUS UX R3.1.

This module is intentionally pure and side-effect free.  It does not read files,
call networks, write state, open PRs, deploy, or mutate databases.

Purpose:
- stop residual WhatsApp / "guided project" footers from leaking into executive
  advisory answers when the user did not explicitly ask for human help;
- keep CTA rendering opt-in through explicit routing metadata.
"""

import copy
import re
from typing import Any, Dict, Iterable, Tuple


MANUS_UX_R3_1_CTA_GUARD_VERSION = "MANUS_UX_R3_1_BACKEND_CTA_SUPPRESSION_V1"


_COMMERCIAL_CTA_MARKERS = (
    "pronto para transformar isso em projeto guiado",
    "ready to turn this into a guided project",
    "a equipe patroai/orkio pode mapear",
    "the patroai/orkio team can map",
    "desenhar os agentes certos",
    "design the right agents",
    "orientar o próximo passo",
    "orientar o proximo passo",
    "falar com a equipe no whatsapp",
    "talk to the team on whatsapp",
    "atendimento humano • orkio/patroai",
    "atendimento humano - orkio/patroai",
    "human support • orkio/patroai",
    "human support - orkio/patroai",
    "botões de implantação",
    "botoes de implantacao",
)

_WHATSAPP_RE = re.compile(
    r"(https?://)?(wa\.me|api\.whatsapp\.com|web\.whatsapp\.com|chat\.whatsapp\.com)/\S+",
    re.IGNORECASE,
)


def _lower(value: Any) -> str:
    return str(value or "").strip().lower()


def _routing(payload: Dict[str, Any]) -> Dict[str, Any]:
    return (
        payload.get("runtime_hints", {}).get("routing")
        or payload.get("metadata", {}).get("routing")
        or payload.get("done_payload", {}).get("runtime_hints", {}).get("routing")
        or payload.get("done_payload", {}).get("metadata", {}).get("routing")
        or {}
    )


def commercial_cta_allowed(payload_or_context: Any = None) -> bool:
    """Return True only when CTA was explicitly allowed by routing/context."""

    if not isinstance(payload_or_context, dict):
        return False

    routing = _routing(payload_or_context)
    return bool(
        payload_or_context.get("commercial_cta_allowed") is True
        or payload_or_context.get("allow_commercial_cta") is True
        or payload_or_context.get("human_help_intent") is True
        or payload_or_context.get("metadata", {}).get("commercial_cta_allowed") is True
        or routing.get("commercial_cta_allowed") is True
        or routing.get("human_help_intent") is True
    )


def has_commercial_cta_signature(value: Any) -> bool:
    text = _lower(value)
    if not text:
        return False
    if _WHATSAPP_RE.search(text):
        return True
    return any(marker in text for marker in _COMMERCIAL_CTA_MARKERS)


def strip_unrequested_commercial_cta(value: Any, *, allow: bool = False) -> str:
    """Remove residual commercial CTA blocks unless allow=True.

    Strategy is conservative:
    - if no known CTA signature exists, return original text;
    - if a known CTA line exists, remove from first CTA line to the end;
    - if only a WhatsApp URL is embedded, remove the URL and clean blank lines.
    """

    text = str(value or "")
    if allow or not text:
        return text
    if not has_commercial_cta_signature(text):
        return text

    lines = text.splitlines()
    first_cta_index = None
    for idx, line in enumerate(lines):
        if has_commercial_cta_signature(line):
            first_cta_index = idx
            break

    if first_cta_index is not None:
        return "\n".join(lines[:first_cta_index]).rstrip()

    # Fallback for inline URLs.
    cleaned = _WHATSAPP_RE.sub("", text)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


def enforce_backend_cta_policy(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    """Return a sanitized deep copy and whether text was modified."""

    if not isinstance(payload, dict):
        return payload, False

    out = copy.deepcopy(payload)
    allow = commercial_cta_allowed(out)
    changed = False

    for key in ("answer", "message", "final_text", "response_text", "content", "text"):
        if key in out and isinstance(out.get(key), str):
            cleaned = strip_unrequested_commercial_cta(out[key], allow=allow)
            if cleaned != out[key]:
                out[key] = cleaned
                changed = True

    # Normalize explicit policy flags for advisory routes.
    if not allow:
        out["commercial_cta_allowed"] = False
        out["commercial_cta_suppressed"] = True

        runtime_hints = out.setdefault("runtime_hints", {})
        routing = runtime_hints.setdefault("routing", {})
        routing["commercial_cta_allowed"] = False
        routing["commercial_cta_suppressed"] = True
        routing["backend_cta_guard_version"] = MANUS_UX_R3_1_CTA_GUARD_VERSION

        metadata = out.setdefault("metadata", {})
        metadata["commercial_cta_allowed"] = False
        metadata["commercial_cta_suppressed"] = True
        metadata["backend_cta_guard_version"] = MANUS_UX_R3_1_CTA_GUARD_VERSION

    out["backend_cta_sanitized"] = bool(changed)
    return out, changed
