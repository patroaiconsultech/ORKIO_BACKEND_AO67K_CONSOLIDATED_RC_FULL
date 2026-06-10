from __future__ import annotations

"""
AO67C — Agent Knowledge Base Primitives

Primitivos compartilhados para perfis, conhecimento e hooks de agentes.

Regras:
- Dados declarativos e auditáveis.
- Nenhum agente interno ganha identidade pública.
- Todo payload público resolve para Orkio.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence


AGENT_KNOWLEDGE_BASE_VERSION = "AO67C_AGENT_KNOWLEDGE_BASE_V1"
PUBLIC_VISIBLE_AGENT_ID = "orkio"
PUBLIC_VISIBLE_AGENT_NAME = "Orkio"


def strip_accents(value: Any) -> str:
    raw = str(value or "")
    normalized = unicodedata.normalize("NFD", raw)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_text(value: Any) -> str:
    raw = strip_accents(value).lower()
    raw = re.sub(r"[^a-z0-9_@/\-\s]+", " ", raw)
    return re.sub(r"\s+", " ", raw).strip()


def contains_any(text: Any, markers: Iterable[str]) -> bool:
    normalized = normalize_text(text)
    return any(normalize_text(marker) in normalized for marker in markers if str(marker or "").strip())


def score_markers(text: Any, markers: Iterable[str]) -> float:
    normalized = normalize_text(text)
    if not normalized:
        return 0.0

    hits = 0
    strong_hits = 0
    for marker in markers or []:
        marker_norm = normalize_text(marker)
        if not marker_norm:
            continue
        if marker_norm in normalized:
            hits += 1
            if " " in marker_norm or len(marker_norm) >= 8:
                strong_hits += 1

    if hits <= 0:
        return 0.0

    return round(min(0.94, 0.28 + hits * 0.14 + strong_hits * 0.18), 3)


@dataclass(frozen=True)
class AgentProfile:
    agent_id: str
    display_name: str
    public_visible: bool = False
    resolve_to_public_speaker: str = PUBLIC_VISIBLE_AGENT_NAME
    internal_role: str = ""
    mission: str = ""
    domains: tuple[str, ...] = field(default_factory=tuple)
    public_summary: str = "Capacidade interna do Orkio."
    risk_level: str = "low"

    def to_dict(self, *, public: bool = False) -> Dict[str, Any]:
        if public:
            return {
                "agent_id": PUBLIC_VISIBLE_AGENT_ID,
                "display_name": PUBLIC_VISIBLE_AGENT_NAME,
                "public_visible": True,
                "resolve_to_public_speaker": PUBLIC_VISIBLE_AGENT_NAME,
                "public_summary": "Orkio conduz a experiência pública e pode usar capacidades internas de forma invisível.",
            }

        return {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "public_visible": bool(self.public_visible),
            "resolve_to_public_speaker": self.resolve_to_public_speaker or PUBLIC_VISIBLE_AGENT_NAME,
            "internal_role": self.internal_role,
            "mission": self.mission,
            "domains": list(self.domains),
            "public_summary": self.public_summary,
            "risk_level": self.risk_level,
        }


@dataclass(frozen=True)
class KnowledgeCard:
    card_id: str
    agent_id: str
    title: str
    summary: str
    domains: tuple[str, ...] = field(default_factory=tuple)
    triggers: tuple[str, ...] = field(default_factory=tuple)
    public_safe: bool = False
    internal_only: bool = True
    priority: int = 100

    def score(self, message: Any) -> float:
        return score_markers(message, self.triggers)

    def to_dict(self, *, public: bool = False, include_triggers: bool = False) -> Dict[str, Any]:
        if public:
            return {
                "card_id": self.card_id,
                "agent_id": PUBLIC_VISIBLE_AGENT_ID,
                "visible_agent": PUBLIC_VISIBLE_AGENT_NAME,
                "title": "capacidade interna do Orkio",
                "summary": "Sinal interno usado pelo Orkio para conduzir melhor a resposta, sem expor especialistas.",
                "domains": list(self.domains),
                "public_safe": bool(self.public_safe),
                "internal_only": bool(self.internal_only),
                "priority": self.priority,
            }

        data = {
            "card_id": self.card_id,
            "agent_id": self.agent_id,
            "visible_agent": PUBLIC_VISIBLE_AGENT_NAME,
            "title": self.title,
            "summary": self.summary,
            "domains": list(self.domains),
            "public_safe": bool(self.public_safe),
            "internal_only": bool(self.internal_only),
            "priority": self.priority,
        }
        if include_triggers:
            data["triggers"] = list(self.triggers)
        return data


@dataclass(frozen=True)
class AgentHook:
    hook_id: str
    agent_id: str
    family: str
    label: str
    description: str
    triggers: tuple[str, ...] = field(default_factory=tuple)
    priority: int = 100
    public_safe: bool = False
    internal_only: bool = True
    synthesis_role: str = "internal_signal"

    def score(self, message: Any) -> float:
        return score_markers(message, self.triggers)

    def to_dict(self, *, public: bool = False, include_triggers: bool = False) -> Dict[str, Any]:
        if public:
            return {
                "hook_id": self.hook_id,
                "agent_id": PUBLIC_VISIBLE_AGENT_ID,
                "family": self.family,
                "label": "capacidade interna do Orkio",
                "description": "Sinal interno usado pelo Orkio sem expor especialistas.",
                "priority": self.priority,
                "public_safe": bool(self.public_safe),
                "internal_only": bool(self.internal_only),
                "visible_agent": PUBLIC_VISIBLE_AGENT_NAME,
                "synthesis_role": self.synthesis_role,
            }

        data = {
            "hook_id": self.hook_id,
            "agent_id": self.agent_id,
            "family": self.family,
            "label": self.label,
            "description": self.description,
            "priority": self.priority,
            "public_safe": bool(self.public_safe),
            "internal_only": bool(self.internal_only),
            "visible_agent": PUBLIC_VISIBLE_AGENT_NAME,
            "synthesis_role": self.synthesis_role,
        }
        if include_triggers:
            data["triggers"] = list(self.triggers)
        return data


def build_internal_advice(
    *,
    agent_id: str,
    message: Any,
    profile: AgentProfile,
    cards: Sequence[KnowledgeCard],
    hooks: Sequence[AgentHook],
    max_cards: int = 3,
    max_hooks: int = 3,
) -> Dict[str, Any]:
    scored_cards: List[Dict[str, Any]] = []
    for card in cards or []:
        score = card.score(message)
        if score <= 0:
            continue
        payload = card.to_dict(public=False, include_triggers=False)
        payload["score"] = score
        scored_cards.append(payload)

    scored_hooks: List[Dict[str, Any]] = []
    for hook in hooks or []:
        score = hook.score(message)
        if score <= 0:
            continue
        payload = hook.to_dict(public=False, include_triggers=False)
        payload["score"] = score
        scored_hooks.append(payload)

    scored_cards.sort(key=lambda item: (-float(item.get("score") or 0), int(item.get("priority") or 100)))
    scored_hooks.sort(key=lambda item: (-float(item.get("score") or 0), int(item.get("priority") or 100)))

    confidence = 0.0
    if scored_cards or scored_hooks:
        scores = [float(item.get("score") or 0.0) for item in scored_cards[:max_cards] + scored_hooks[:max_hooks]]
        confidence = round(min(0.96, max(scores) if scores else 0.0), 3)

    return {
        "ok": True,
        "service": "agent_knowledge_advice",
        "version": AGENT_KNOWLEDGE_BASE_VERSION,
        "agent_id": agent_id,
        "agent_display_name": profile.display_name,
        "public_visible": False if agent_id != PUBLIC_VISIBLE_AGENT_ID else True,
        "resolve_to_public_speaker": PUBLIC_VISIBLE_AGENT_NAME,
        "confidence": confidence,
        "matched_cards": scored_cards[:max_cards],
        "matched_hooks": scored_hooks[:max_hooks],
        "public_payload": {
            "agent_id": PUBLIC_VISIBLE_AGENT_ID,
            "agent_name": PUBLIC_VISIBLE_AGENT_NAME,
            "visible_agent": PUBLIC_VISIBLE_AGENT_NAME,
            "final_speaker": PUBLIC_VISIBLE_AGENT_NAME,
        },
    }


def public_safe_agent_payload(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    data = dict(payload or {})
    data.update({
        "agent_id": PUBLIC_VISIBLE_AGENT_ID,
        "agent_name": PUBLIC_VISIBLE_AGENT_NAME,
        "visible_agent": PUBLIC_VISIBLE_AGENT_NAME,
        "final_speaker": PUBLIC_VISIBLE_AGENT_NAME,
        "resolve_to_public_speaker": PUBLIC_VISIBLE_AGENT_NAME,
    })
    return data
