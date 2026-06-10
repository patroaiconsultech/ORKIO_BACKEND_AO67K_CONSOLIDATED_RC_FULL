from __future__ import annotations

"""
AO67H — Quality Gate Bridge

Purpose:
- Prevent duplicated blocking between:
  AO67A visibility_policy,
  AO67B decision_mesh,
  AO67F chat gateway,
  AO67G orchestration_quality_gate.
- Centralize public surface validation into a single idempotent bridge.
- No LLM call, no DB write, no network call.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


PUBLIC_SPEAKER = "Orkio"
BRIDGE_MARKER = "ao67h_quality_bridge_checked"


BLOCKED_PUBLIC_NAMES = {
    "chris",
    "orion",
    "cfo",
    "cto",
    "planner",
    "auditor",
    "architect",
    "devops",
    "sre",
    "security",
}


@dataclass(frozen=True)
class QualityBridgeDecision:
    ok: bool
    public_speaker: str = PUBLIC_SPEAKER
    marker: str = BRIDGE_MARKER
    blocked: bool = False
    rewritten: bool = False
    warnings: List[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return str(value)
    except Exception:
        return ""


def _payload_get(payload: Any, key: str, default: Any = None) -> Any:
    if isinstance(payload, dict):
        return payload.get(key, default)
    return getattr(payload, key, default)


def _payload_set(payload: Any, key: str, value: Any) -> Any:
    if isinstance(payload, dict):
        payload[key] = value
    else:
        try:
            setattr(payload, key, value)
        except Exception:
            pass
    return payload


def has_bridge_marker(payload: Any) -> bool:
    return bool(_payload_get(payload, BRIDGE_MARKER, False))


def mark_bridge_checked(payload: Any) -> Any:
    return _payload_set(payload, BRIDGE_MARKER, True)


def run_public_surface_quality_bridge(
    payload: Any,
    *,
    candidate_text: Any = "",
    surface: str = "public",
    allow_admin_names: bool = False,
    **_: Any,
) -> QualityBridgeDecision:
    """
    Idempotent guard for public response surface.

    This does not replace deeper governance. It makes sure only one public
    surface check is counted for AO67F/AO67G integration.
    """
    if has_bridge_marker(payload):
        return QualityBridgeDecision(
            ok=True,
            blocked=False,
            rewritten=False,
            reason="already_checked",
        )

    mark_bridge_checked(payload)

    norm_surface = str(surface or "public").strip().lower()
    if norm_surface in {"admin", "founder", "internal", "operator"} and allow_admin_names:
        return QualityBridgeDecision(
            ok=True,
            blocked=False,
            rewritten=False,
            reason="admin_surface_names_allowed",
        )

    text = _text(candidate_text).lower()
    leaked = sorted([name for name in BLOCKED_PUBLIC_NAMES if name in text])
    if leaked:
        return QualityBridgeDecision(
            ok=False,
            blocked=True,
            rewritten=True,
            warnings=[f"public_internal_name_detected:{name}" for name in leaked],
            reason="public_internal_agent_name_blocked",
        )

    return QualityBridgeDecision(
        ok=True,
        blocked=False,
        rewritten=False,
        reason="public_surface_ok",
    )
