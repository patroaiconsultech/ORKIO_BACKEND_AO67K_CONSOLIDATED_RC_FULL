from __future__ import annotations

"""
AO67C — Agent Knowledge Registry

Registro interno de conhecimento dos agentes.

Não é catálogo público.
Não deve ser exposto em /api/agents para usuários públicos.
Serve para AO67B/AO67C/AO67D alimentarem o Orkio Decision Mesh com sinais invisíveis.
"""

from typing import Any, Dict, Iterable, List, Optional

from app.agents.base import (
    PUBLIC_VISIBLE_AGENT_ID,
    PUBLIC_VISIBLE_AGENT_NAME,
    public_safe_agent_payload,
)

from .orkio import advise as orkio_advise
from .orkio import get_hooks as orkio_hooks
from .orkio import get_knowledge_cards as orkio_cards
from .orkio import get_profile as orkio_profile

from .chris import advise as chris_advise
from .chris import get_hooks as chris_hooks
from .chris import get_knowledge_cards as chris_cards
from .chris import get_profile as chris_profile

from .orion import advise as orion_advise
from .orion import get_hooks as orion_hooks
from .orion import get_knowledge_cards as orion_cards
from .orion import get_profile as orion_profile


AGENT_KNOWLEDGE_REGISTRY_VERSION = "AO67C_AGENT_KNOWLEDGE_REGISTRY_V1"

_AGENT_MODULES = {
    "orkio": {
        "profile": orkio_profile,
        "cards": orkio_cards,
        "hooks": orkio_hooks,
        "advise": orkio_advise,
    },
    "chris": {
        "profile": chris_profile,
        "cards": chris_cards,
        "hooks": chris_hooks,
        "advise": chris_advise,
    },
    "orion": {
        "profile": orion_profile,
        "cards": orion_cards,
        "hooks": orion_hooks,
        "advise": orion_advise,
    },
}


def list_agent_profiles(*, public: bool = False) -> List[Dict[str, Any]]:
    profiles: List[Dict[str, Any]] = []
    if public:
        return [public_safe_agent_payload({
            "public_summary": "Orkio conduz a experiência pública. Capacidades internas podem apoiar a resposta sem virar personas públicas."
        })]

    for module in _AGENT_MODULES.values():
        profile = module["profile"]()
        profiles.append(profile.to_dict(public=False))
    return profiles


def get_agent_profile(agent_id: str, *, public: bool = False) -> Optional[Dict[str, Any]]:
    key = str(agent_id or "").strip().lower()
    if public:
        return public_safe_agent_payload()
    module = _AGENT_MODULES.get(key)
    if not module:
        return None
    return module["profile"]().to_dict(public=False)


def collect_agent_hooks(*, public: bool = False, include_internal: bool = True) -> List[Dict[str, Any]]:
    hooks: List[Dict[str, Any]] = []
    if public:
        return []

    for module in _AGENT_MODULES.values():
        for hook in module["hooks"]():
            if hook.internal_only and not include_internal:
                continue
            hooks.append(hook.to_dict(public=False, include_triggers=False))

    hooks.sort(key=lambda item: (int(item.get("priority") or 100), str(item.get("hook_id") or "")))
    return hooks


def collect_knowledge_cards(*, public: bool = False, include_internal: bool = True) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    if public:
        return []

    for module in _AGENT_MODULES.values():
        for card in module["cards"]():
            if card.internal_only and not include_internal:
                continue
            cards.append(card.to_dict(public=False, include_triggers=False))

    cards.sort(key=lambda item: (int(item.get("priority") or 100), str(item.get("card_id") or "")))
    return cards


def collect_agent_advice(
    message: Any,
    *,
    context: Optional[Dict[str, Any]] = None,
    include_agents: Optional[Iterable[str]] = None,
    min_confidence: float = 0.20,
) -> Dict[str, Any]:
    requested = {str(item or "").strip().lower() for item in include_agents or [] if str(item or "").strip()}
    if not requested:
        requested = set(_AGENT_MODULES.keys())

    advice_items: List[Dict[str, Any]] = []
    for agent_id in sorted(requested):
        module = _AGENT_MODULES.get(agent_id)
        if not module:
            continue
        advice = module["advise"](message, context or {})
        if float(advice.get("confidence") or 0.0) < float(min_confidence or 0.0):
            continue
        advice_items.append(advice)

    advice_items.sort(key=lambda item: (-float(item.get("confidence") or 0), str(item.get("agent_id") or "")))

    return {
        "ok": True,
        "service": "agent_knowledge_registry",
        "version": AGENT_KNOWLEDGE_REGISTRY_VERSION,
        "public_visible_agent_id": PUBLIC_VISIBLE_AGENT_ID,
        "public_visible_agent_name": PUBLIC_VISIBLE_AGENT_NAME,
        "resolve_to_public_speaker": PUBLIC_VISIBLE_AGENT_NAME,
        "advice_count": len(advice_items),
        "advice": advice_items,
        "public_payload": public_safe_agent_payload(),
    }


def build_agent_knowledge_snapshot(message: Any, *, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    advice = collect_agent_advice(message, context=context)
    return {
        "ok": True,
        "service": "agent_knowledge_snapshot",
        "version": AGENT_KNOWLEDGE_REGISTRY_VERSION,
        "profiles": list_agent_profiles(public=False),
        "matched_advice": advice.get("advice") or [],
        "public_payload": public_safe_agent_payload(),
        "visibility_contract": {
            "public_speaker": PUBLIC_VISIBLE_AGENT_NAME,
            "internal_agents_public_visible": False,
            "rule": "specialists_advise_orkio_decides_orkio_answers",
        },
    }
