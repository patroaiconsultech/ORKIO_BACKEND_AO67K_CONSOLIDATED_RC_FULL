from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?\d{4,5}[-\s]?\d{4}(?!\d)")
CPF_RE = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")


@dataclass(frozen=True)
class PrivacyScanResult:
    has_pii: bool
    pii_types: list[str] = field(default_factory=list)
    redacted_text: str = ""
    redaction_status: str = "clean"

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_pii": self.has_pii,
            "pii_types": list(self.pii_types),
            "redacted_text": self.redacted_text,
            "redaction_status": self.redaction_status,
        }


class PrivacyScanner:
    def scan(self, text: str) -> PrivacyScanResult:
        working = text or ""
        pii_types: list[str] = []

        if EMAIL_RE.search(working):
            pii_types.append("email")
            working = EMAIL_RE.sub("[REDACTED_EMAIL]", working)

        if CPF_RE.search(working):
            pii_types.append("cpf")
            working = CPF_RE.sub("[REDACTED_CPF]", working)

        if PHONE_RE.search(working):
            pii_types.append("phone")
            working = PHONE_RE.sub("[REDACTED_PHONE]", working)

        has_pii = bool(pii_types)
        return PrivacyScanResult(
            has_pii=has_pii,
            pii_types=pii_types,
            redacted_text=working,
            redaction_status="redacted" if has_pii else "clean",
        )
