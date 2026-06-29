from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_conversation_text(text: str) -> str:
    return " ".join((text or "").strip().split())


def build_content_hash(text: str) -> str:
    normalized = normalize_conversation_text(text)
    return sha256(normalized.encode("utf-8")).hexdigest()


def build_idempotency_key(
    *,
    tenant_id: str,
    thread_id: str,
    conversation_text: str,
    schema_version: str = "oep004.3",
) -> str:
    seed = "|".join(
        [
            schema_version,
            str(tenant_id or "").strip(),
            str(thread_id or "").strip(),
            build_content_hash(conversation_text),
        ]
    )
    return sha256(seed.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ConversationIntake:
    conversation_text: str
    tenant_id: str
    user_id: str
    thread_id: str
    conversation_id: str | None = None
    consent_granted: bool = False
    retention_policy: str = "standard"
    source: str = "manual"
    schema_version: str = "oep004.3"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)

    def validate(self) -> None:
        if not normalize_conversation_text(self.conversation_text):
            raise ValueError("conversation_text is required")
        if not str(self.tenant_id or "").strip():
            raise ValueError("tenant_id is required")
        if not str(self.user_id or "").strip():
            raise ValueError("user_id is required")
        if not str(self.thread_id or "").strip():
            raise ValueError("thread_id is required")
        if self.consent_granted is not True:
            raise PermissionError("consent_granted must be True before distillation")
        if self.retention_policy not in {"none", "short", "standard", "long"}:
            raise ValueError("retention_policy must be one of: none, short, standard, long")

    @property
    def content_hash(self) -> str:
        return build_content_hash(self.conversation_text)

    @property
    def idempotency_key(self) -> str:
        return build_idempotency_key(
            tenant_id=self.tenant_id,
            thread_id=self.thread_id,
            conversation_text=self.conversation_text,
            schema_version=self.schema_version,
        )

    def to_payload(self) -> dict[str, Any]:
        self.validate()
        payload = asdict(self)
        payload["content_hash"] = self.content_hash
        payload["idempotency_key"] = self.idempotency_key
        payload["normalized_text"] = normalize_conversation_text(self.conversation_text)
        payload["proposal_only"] = True
        payload["write_executed"] = False
        payload["human_approval_required"] = True
        return payload


class ConversationIntakeValidator:
    def validate(self, intake: ConversationIntake) -> dict[str, Any]:
        return intake.to_payload()
