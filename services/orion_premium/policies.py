"""Feature flags and immutable Phase 1 policy defaults."""

from __future__ import annotations

import os


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


DOCUMENT_EVIDENCE_GUARD_ENABLED = _env_bool(
    "ORION_DOCUMENT_EVIDENCE_GUARD_ENABLED",
    True,
)
SHADOW_MODE = _env_bool("ORION_PREMIUM_SHADOW_MODE", True)
REQUIRE_EXECUTION_RECEIPT = _env_bool(
    "ORION_REQUIRE_EXECUTION_RECEIPT",
    True,
)
REQUIRE_HUMAN_APPROVAL = _env_bool(
    "ORION_REQUIRE_HUMAN_APPROVAL",
    True,
)

MIN_LEARNING_CONFIDENCE = float(
    os.getenv("ORION_MIN_LEARNING_CONFIDENCE", "0.70")
)
