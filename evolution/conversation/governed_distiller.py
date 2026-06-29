from __future__ import annotations

from typing import Any

from evolution.conversation.intake import ConversationIntake, ConversationIntakeValidator
from evolution.conversation.privacy import PrivacyScanner


class GovernedConversationDistiller:
    """
    OEP-004.3 guarded intake wrapper.

    This wrapper intentionally does not integrate with chat, realtime, voice,
    database, or background jobs. It validates metadata and privacy posture
    before delegating to an existing distiller object.
    """

    def __init__(self, distiller: Any, privacy_scanner: PrivacyScanner | None = None) -> None:
        self._distiller = distiller
        self._validator = ConversationIntakeValidator()
        self._privacy = privacy_scanner or PrivacyScanner()

    def distill_intake(self, intake: ConversationIntake) -> dict[str, Any]:
        payload = self._validator.validate(intake)
        scan = self._privacy.scan(payload["normalized_text"])

        text_for_distillation = scan.redacted_text
        result = self._distiller.distill(text_for_distillation)

        return {
            "intake": payload,
            "privacy": scan.to_dict(),
            "distillation": result.to_dict() if hasattr(result, "to_dict") else result,
            "proposal_only": True,
            "write_executed": False,
            "human_approval_required": True,
        }
