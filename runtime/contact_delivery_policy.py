"""
AO67I — Contact Delivery Policy

Public-safe policy for the `/api/public/contact` flow.

Purpose:
- Keep contact form storage independent from email delivery.
- Make email delivery observable and testable.
- Avoid silent success when Resend is not configured.
- Preserve public UX by default: contact submission is accepted even if email delivery fails.
- Allow strict mode only when explicitly configured.

No network, DB, LLM or deployment side effects in this module.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict


def _clean_env(value: Any, *, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    if not text:
        return default
    if len(text) >= 2 and ((text[0] == text[-1] == '"') or (text[0] == text[-1] == "'")):
        text = text[1:-1].strip()
    return text or default


def _env_bool(key: str, default: bool = False) -> bool:
    raw = _clean_env(os.getenv(key, ""))
    if raw == "":
        return default
    return raw.lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class ContactDeliveryPolicy:
    provider: str
    configured: bool
    required: bool
    send_internal: bool
    send_confirmation: bool
    internal_to_present: bool
    from_present: bool
    max_message_chars: int

    def public_status_for(self, *, internal_ok: bool, confirmation_ok: bool) -> str:
        if not self.configured:
            return "not_configured"
        if self.send_internal and self.send_confirmation:
            if internal_ok and confirmation_ok:
                return "sent"
            if internal_ok or confirmation_ok:
                return "partial"
            return "failed"
        if self.send_internal:
            return "sent" if internal_ok else "failed"
        if self.send_confirmation:
            return "sent" if confirmation_ok else "failed"
        return "disabled"

    def to_safe_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "configured": self.configured,
            "required": self.required,
            "send_internal": self.send_internal,
            "send_confirmation": self.send_confirmation,
            "internal_to_present": self.internal_to_present,
            "from_present": self.from_present,
            "max_message_chars": self.max_message_chars,
        }


def load_contact_delivery_policy() -> ContactDeliveryPolicy:
    api_key = _clean_env(os.getenv("RESEND_API_KEY", ""))
    internal_to = _clean_env(os.getenv("RESEND_INTERNAL_TO", ""))
    from_email = _clean_env(os.getenv("RESEND_FROM", ""))

    send_internal = _env_bool("ORKIO_CONTACT_SEND_INTERNAL", True)
    send_confirmation = _env_bool("ORKIO_CONTACT_SEND_CONFIRMATION", True)
    required = _env_bool("ORKIO_CONTACT_EMAIL_REQUIRED", False)

    try:
        max_message_chars = int(_clean_env(os.getenv("ORKIO_CONTACT_EMAIL_MAX_MESSAGE_CHARS", "4000"), default="4000"))
    except Exception:
        max_message_chars = 4000
    max_message_chars = max(500, min(max_message_chars, 12000))

    configured = bool(api_key and internal_to and from_email)

    return ContactDeliveryPolicy(
        provider="resend",
        configured=configured,
        required=required,
        send_internal=send_internal,
        send_confirmation=send_confirmation,
        internal_to_present=bool(internal_to),
        from_present=bool(from_email),
        max_message_chars=max_message_chars,
    )
