from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional

from app.core.premium_agent_standard import evaluate_premium_response


def apply_orchestration_quality_gate(
    *,
    user_message: str,
    draft_response: str,
    agent_name: Optional[str] = None,
    public_surface: bool = True,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Apply the AO67G quality gate to an orchestration draft.

    This does not call a model and does not mutate state.
    It returns a decision object the chat gateway can use later.
    """

    context = deepcopy(context or {})
    quality = evaluate_premium_response(
        user_message=user_message,
        draft_response=draft_response,
        public_surface=public_surface,
        agent_name=agent_name,
        context=context,
    )

    final_speaker = "Orkio" if public_surface else (agent_name or "Orkio")
    allow_public_emit = bool(quality.get("passed"))

    fallback_response = (
        "Vou conduzir isso com segurança pelo Orkio. Para te entregar uma resposta precisa, "
        "me diga o objetivo principal, o contexto atual e qual decisão você precisa tomar agora."
    )

    return {
        "version": "AO67G-v1",
        "allow_public_emit": allow_public_emit,
        "final_speaker": final_speaker,
        "public_agent_name": "Orkio" if public_surface else final_speaker,
        "quality": quality,
        "safe_fallback_response": "" if allow_public_emit else fallback_response,
        "requires_revision": not allow_public_emit,
        "blocked_by": list(quality.get("blocked_by") or []),
    }
