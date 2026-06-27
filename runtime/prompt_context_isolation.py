# PATCH37_REV_B_PREMIUM_CONTEXT_ISOLATION_ALL_SENDS
# Arquivo sugerido: backend/runtime/prompt_context_isolation.py

from __future__ import annotations

import re
from typing import Any, Dict

PATCH_37_REV_B_CONTEXT_ISOLATION_ALL_SENDS_VERSION = (
    "PATCH_37_REV_B_PREMIUM_CONTEXT_ISOLATION_ALL_SENDS_V1"
)

_INTERNAL_RUNTIME_MARKERS = (
    "PREFERENCIA_DE_TRATAMENTO_DO_USUARIO",
    "PROFILE_ADDRESS_PREFERENCE",
    "MENSAGEM_DO_USUARIO:",
    "PATCH_32",
    "PATCH_33",
    "PATCH_34",
    "PATCH_35",
    "PATCH_36",
    "PATCH_37",
    "@Orkio orchestration_audit",
    "@Orion orchestration_audit",
    "@Chris orchestration_audit",
    "@Laura orchestration_audit",
    "Origem: Realtime voice transcript.final",
    "Modo: readonly",
    "Regra crítica:",
)

_ORCHESTRATION_AUDIT_RE = re.compile(
    r"^\s*@(Orkio|Orion|Chris|Laura)\s+orchestration_audit\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def has_internal_runtime_envelope(value: Any) -> bool:
    raw = str(value or "")
    if not raw:
        return False
    return any(marker in raw for marker in _INTERNAL_RUNTIME_MARKERS)


def strip_internal_runtime_envelope(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""

    marker = "MENSAGEM_DO_USUARIO:"
    if marker in raw:
        raw = raw.rsplit(marker, 1)[-1].strip()

    raw = re.sub(
        r"^\s*PREFERENCIA_DE_TRATAMENTO_DO_USUARIO[\s\S]*?(?=\n\s*\n|$)",
        "",
        raw,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    raw = re.sub(
        r"^\s*PROFILE_ADDRESS_PREFERENCE[\s\S]*?(?=\n\s*\n|$)",
        "",
        raw,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    raw = re.sub(
        r"^\s*PATCH_\d+[^\n]*(?:\n(?!\s*(?:@|Origem:|Modo:|Regra crítica:|MENSAGEM_DO_USUARIO:)).*)*",
        "",
        raw,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    raw = _ORCHESTRATION_AUDIT_RE.sub("", raw)
    raw = re.sub(r"^\s*Origem:\s*Realtime voice transcript\.final\s*$", "", raw, flags=re.IGNORECASE | re.MULTILINE)
    raw = re.sub(r"^\s*Modo:\s*readonly\s*$", "", raw, flags=re.IGNORECASE | re.MULTILINE)
    raw = re.sub(r"^\s*Regra crítica:[^\n]*$", "", raw, flags=re.IGNORECASE | re.MULTILINE)

    return raw.strip()


def sanitize_inbound_user_message(value: Any, meta: Dict[str, Any] | None = None) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    if not has_internal_runtime_envelope(text):
        return text

    clean = strip_internal_runtime_envelope(text)

    if isinstance(meta, dict):
        meta["prompt_context_isolation_version"] = PATCH_37_REV_B_CONTEXT_ISOLATION_ALL_SENDS_VERSION
        meta["internal_runtime_envelope_stripped"] = True
        meta["original_message_length"] = len(text)
        meta["clean_message_length"] = len(clean)

    return clean
