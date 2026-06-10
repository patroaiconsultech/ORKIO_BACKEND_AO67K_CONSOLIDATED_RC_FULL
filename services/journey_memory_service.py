# AO67D — Journey Memory service facade
# Destino real: app/services/journey_memory_service.py
# Modo: PATCH_PREMIUM / foundation-only / no main.py wiring
#
from __future__ import annotations

from typing import Any, Dict, Optional

from app.runtime.journey_memory import detect_journey_track
from app.runtime.journey_memory_persistence import (
    build_journey_memory_context,
    update_public_journey_memory,
)


def detect_public_journey_signal(message: Any) -> Dict[str, Any]:
    """Facade estável para testes e integrações futuras."""
    return detect_journey_track(message).to_dict()


def update_public_journey_from_message(
    db: Any,
    *,
    message: Any,
    org_slug: str = "public",
    user_id: Optional[str] = None,
    thread_id: Optional[str] = None,
    commit: bool = False,
) -> Dict[str, Any]:
    """Detecta sinal de jornada e persiste snapshot público-seguro."""
    signal = detect_journey_track(message)
    return update_public_journey_memory(
        db,
        signal,
        org_slug=org_slug,
        user_id=user_id,
        thread_id=thread_id,
        commit=commit,
    )


def get_public_journey_context(
    db: Any,
    *,
    org_slug: str = "public",
    user_id: Optional[str] = None,
    thread_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Carrega contexto compacto para Decision Mesh / Orkio overlay."""
    return build_journey_memory_context(
        db,
        org_slug=org_slug,
        user_id=user_id,
        thread_id=thread_id,
    )
