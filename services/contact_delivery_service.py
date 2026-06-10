"""
AO67I — Contact Delivery Reliability Service

Service layer for contact form email notifications.

This module is designed to be plugged into `app/main.py` with a small, reversible
wiring around `/api/public/contact`.

Design:
- No DB writes here.
- No framework imports.
- No direct dependency on FastAPI.
- Uses the existing `_send_resend_email` function when injected by `main.py`.
- Logs observable, non-secret delivery events.
- Keeps public response safe and avoids leaking internal recipients or provider errors.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Callable, Dict, Optional

from app.runtime.contact_delivery_policy import load_contact_delivery_policy, _clean_env


SendEmailFn = Callable[..., bool]


@dataclass
class ContactNotificationPayload:
    contact_id: str
    full_name: str
    email: str
    whatsapp: str
    subject: str
    message: str
    privacy_request_type: Optional[str]
    consent_terms: bool
    consent_marketing: bool
    ip: str
    user_agent: str
    terms_version: str
    created_at: int


@dataclass
class ContactDeliveryResult:
    ok: bool
    configured: bool
    required: bool
    internal_ok: bool
    confirmation_ok: bool
    public_status: str
    contact_id: str
    provider: str = "resend"

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "status": self.public_status,
            "configured": self.configured,
            "contact_id": self.contact_id,
        }

    def to_log_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "configured": self.configured,
            "required": self.required,
            "internal_ok": self.internal_ok,
            "confirmation_ok": self.confirmation_ok,
            "public_status": self.public_status,
            "contact_id": self.contact_id,
            "provider": self.provider,
        }


def _truncate(value: str, max_chars: int) -> str:
    text = str(value or "")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[message truncated by contact delivery policy]"


def _internal_subject(payload: ContactNotificationPayload) -> str:
    subject = (payload.subject or "").strip()
    if subject.lower() == "data privacy request" and payload.privacy_request_type:
        return f"[ORKIO – PRIVACY] Request – {payload.privacy_request_type}"
    return f"[ORKIO] New Contact – {subject or 'Contact'}"


def _internal_text(payload: ContactNotificationPayload, max_message_chars: int) -> str:
    return (
        "New contact request\n\n"
        f"Contact ID: {payload.contact_id}\n"
        f"Name: {payload.full_name}\n"
        f"Email: {payload.email}\n"
        f"WhatsApp: {payload.whatsapp or ''}\n"
        f"Subject: {payload.subject}\n"
        f"Privacy request type: {payload.privacy_request_type or ''}\n"
        f"Consent terms: {payload.consent_terms}\n"
        f"Consent marketing: {payload.consent_marketing}\n"
        f"IP: {payload.ip}\n"
        f"User-Agent: {payload.user_agent}\n"
        f"Terms version: {payload.terms_version}\n"
        f"Created at (UTC ts): {payload.created_at}\n\n"
        "Message:\n"
        f"{_truncate(payload.message, max_message_chars)}\n"
    )


def _confirmation_subject(payload: ContactNotificationPayload) -> str:
    if (payload.subject or "").strip().lower() == "data privacy request":
        return "Recebemos sua solicitação de privacidade – Orkio"
    return "Recebemos sua mensagem – Orkio"


def _confirmation_text(payload: ContactNotificationPayload) -> str:
    return (
        f"Olá {payload.full_name},\n\n"
        "Recebemos sua mensagem pelo formulário de contato do Orkio.\n"
        f"Protocolo: {payload.contact_id}\n\n"
        "Responderemos assim que possível. Para solicitações de privacidade, "
        "o prazo legal de resposta poderá seguir a legislação aplicável.\n\n"
        "Obrigado,\n"
        "Equipe Orkio\n"
    )


def build_contact_notification_payload(**kwargs: Any) -> ContactNotificationPayload:
    return ContactNotificationPayload(
        contact_id=str(kwargs.get("contact_id") or ""),
        full_name=str(kwargs.get("full_name") or "").strip(),
        email=str(kwargs.get("email") or "").strip().lower(),
        whatsapp=str(kwargs.get("whatsapp") or "").strip(),
        subject=str(kwargs.get("subject") or "").strip(),
        message=str(kwargs.get("message") or "").strip(),
        privacy_request_type=kwargs.get("privacy_request_type"),
        consent_terms=bool(kwargs.get("consent_terms")),
        consent_marketing=bool(kwargs.get("consent_marketing")),
        ip=str(kwargs.get("ip") or "unknown"),
        user_agent=str(kwargs.get("user_agent") or ""),
        terms_version=str(kwargs.get("terms_version") or ""),
        created_at=int(kwargs.get("created_at") or 0),
    )


def deliver_contact_notifications(
    payload: ContactNotificationPayload,
    *,
    send_email_fn: SendEmailFn,
    logger: Any = None,
) -> ContactDeliveryResult:
    policy = load_contact_delivery_policy()

    if logger:
        logger.info("CONTACT_DELIVERY_POLICY policy=%s contact_id=%s", policy.to_safe_dict(), payload.contact_id)

    if not policy.configured:
        if logger:
            logger.warning("CONTACT_DELIVERY_NOT_CONFIGURED contact_id=%s policy=%s", payload.contact_id, policy.to_safe_dict())
        status = policy.public_status_for(internal_ok=False, confirmation_ok=False)
        return ContactDeliveryResult(
            ok=not policy.required,
            configured=False,
            required=policy.required,
            internal_ok=False,
            confirmation_ok=False,
            public_status=status,
            contact_id=payload.contact_id,
        )

    internal_ok = False
    confirmation_ok = False

    if policy.send_internal:
        internal_to = _clean_env(os.getenv("RESEND_INTERNAL_TO", ""))
        try:
            internal_ok = bool(
                send_email_fn(
                    internal_to,
                    _internal_subject(payload),
                    _internal_text(payload, policy.max_message_chars),
                )
            )
        except Exception as exc:
            internal_ok = False
            if logger:
                logger.exception("CONTACT_DELIVERY_INTERNAL_FAILED contact_id=%s error=%s", payload.contact_id, str(exc))

    if policy.send_confirmation:
        try:
            confirmation_ok = bool(
                send_email_fn(
                    payload.email,
                    _confirmation_subject(payload),
                    _confirmation_text(payload),
                )
            )
        except Exception as exc:
            confirmation_ok = False
            if logger:
                logger.exception("CONTACT_DELIVERY_CONFIRMATION_FAILED contact_id=%s error=%s", payload.contact_id, str(exc))

    status = policy.public_status_for(internal_ok=internal_ok, confirmation_ok=confirmation_ok)
    ok = status in {"sent", "partial", "disabled"}
    if policy.required:
        ok = status == "sent"

    result = ContactDeliveryResult(
        ok=ok,
        configured=True,
        required=policy.required,
        internal_ok=internal_ok,
        confirmation_ok=confirmation_ok,
        public_status=status,
        contact_id=payload.contact_id,
    )

    if logger:
        log_fn = logger.info if result.ok else logger.warning
        log_fn("CONTACT_DELIVERY_RESULT result=%s", result.to_log_dict())

    return result


def contact_request_status_from_delivery(result: Optional[ContactDeliveryResult]) -> str:
    if result is None:
        return "submitted_email_unknown"
    return f"submitted_email_{result.public_status}"


def public_contact_message(result: Optional[ContactDeliveryResult]) -> str:
    base = (
        "Recebemos sua mensagem. "
        "Responderemos assim que possível. "
        "Para solicitações de privacidade, o prazo de resposta seguirá a legislação aplicável."
    )
    if result is None:
        return base
    if result.public_status == "sent":
        return base + " Um email de confirmação foi enviado."
    if result.public_status == "partial":
        return base + " O protocolo foi registrado; a confirmação por email pode levar alguns minutos."
    if result.public_status in {"not_configured", "failed"}:
        return base + " O protocolo foi registrado."
    return base
