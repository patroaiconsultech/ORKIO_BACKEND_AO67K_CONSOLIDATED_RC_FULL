# AO67D — Journey Memory core
# Destino real: app/runtime/journey_memory.py
# Modo: PATCH_PREMIUM / foundation-only / no main.py wiring
#
# Objetivo:
# - Criar memória de jornada auditável e pública-segura.
# - Manter Orkio como único speaker público.
# - Não chamar LLM, não acessar rede, não executar deploy, não tocar em main.py.
#
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional
import re
import time
import unicodedata


JOURNEY_MEMORY_VERSION = "AO67D_JOURNEY_MEMORY_V1"

PUBLIC_SPEAKER = "Orkio"

TRACK_DEVELOPMENT = "professional_development"
TRACK_SKILLS = "skills_mapping"
TRACK_NETWORKING = "networking"
TRACK_LEADERSHIP = "leadership"
TRACK_INNOVATION = "innovation_ai"
TRACK_ENTREPRENEURSHIP = "entrepreneurship"
TRACK_BUSINESS_DIAGNOSTIC = "business_diagnostic"
TRACK_PLATFORM_EXPLORATION = "platform_exploration"

PUBLIC_JOURNEY_TRACKS = {
    TRACK_DEVELOPMENT: {
        "label": "desenvolvimento profissional",
        "next_question": "Qual habilidade ou posição você quer desenvolver primeiro?",
    },
    TRACK_SKILLS: {
        "label": "mapeamento de skills",
        "next_question": "Quais competências você já usa bem hoje e quais quer fortalecer?",
    },
    TRACK_NETWORKING: {
        "label": "networking e comunidade",
        "next_question": "Que tipo de conexão faria mais diferença para você agora?",
    },
    TRACK_LEADERSHIP: {
        "label": "liderança e comunicação",
        "next_question": "Em qual situação de liderança você quer evoluir primeiro?",
    },
    TRACK_INNOVATION: {
        "label": "inovação e IA no trabalho",
        "next_question": "Qual processo, área ou dor da empresa você quer melhorar com IA?",
    },
    TRACK_ENTREPRENEURSHIP: {
        "label": "empreendedorismo e novos negócios",
        "next_question": "Qual problema você quer resolver e para qual público?",
    },
    TRACK_BUSINESS_DIAGNOSTIC: {
        "label": "diagnóstico de negócio ou projeto",
        "next_question": "Qual resultado você quer melhorar primeiro: vendas, operação, margem, produto ou gestão?",
    },
    TRACK_PLATFORM_EXPLORATION: {
        "label": "exploração guiada da plataforma",
        "next_question": "Você quer testar uma ideia, organizar um plano, mapear skills ou explorar oportunidades?",
    },
}


@dataclass(frozen=True)
class JourneySignal:
    """Sinal público-seguro extraído da fala do usuário.

    Não guarda segredo, prompt técnico, nome interno de agente ou bastidor.
    """

    track: str = TRACK_PLATFORM_EXPLORATION
    intent: str = "exploration"
    goal: str = ""
    focus_area: str = ""
    confidence: float = 0.55
    source: str = "heuristic"
    public_speaker: str = PUBLIC_SPEAKER
    created_at: int = field(default_factory=lambda: int(time.time()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track": self.track,
            "intent": self.intent,
            "goal": self.goal,
            "focus_area": self.focus_area,
            "confidence": round(float(self.confidence or 0.0), 2),
            "source": self.source,
            "public_speaker": PUBLIC_SPEAKER,
            "created_at": int(self.created_at or time.time()),
            "version": JOURNEY_MEMORY_VERSION,
        }


def _strip_accents(value: Any) -> str:
    raw = str(value or "")
    try:
        normalized = unicodedata.normalize("NFD", raw)
        return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    except Exception:
        return raw


def normalize_text(value: Any) -> str:
    raw = _strip_accents(value).lower()
    raw = re.sub(r"[^a-z0-9@:/\.\-_\s]+", " ", raw, flags=re.I)
    return re.sub(r"\s+", " ", raw).strip()


def _contains_any(text: str, markers: Iterable[str]) -> bool:
    return any(marker in text for marker in markers)


def _safe_public_text(value: Any, *, limit: int = 280) -> str:
    text = str(value or "").strip()
    if not text:
        return ""

    blocked = (
        "chris", "orion", "cfo", "cto", "planner", "auditor",
        "runtime", "github", "branch", "pull request", "pr_created",
        "deploy", "patch", "main.py", "app/main.py", "appconsole",
    )
    normalized = normalize_text(text)
    if _contains_any(normalized, blocked):
        return ""

    text = re.sub(r"\s+", " ", text)
    return text[:limit].strip()


def detect_journey_track(message: Any) -> JourneySignal:
    """Detecta trilha pública sem expor agente interno.

    Esta função é determinística e sem dependência externa.
    """

    raw = str(message or "").strip()
    text = normalize_text(raw)

    if not text:
        return JourneySignal()

    if _contains_any(text, ("networking", "network", "conexao", "conexoes", "relacionamento", "comunidade", "amcham")):
        return JourneySignal(
            track=TRACK_NETWORKING,
            intent="improve_networking",
            goal=_safe_public_text(raw),
            focus_area="networking",
            confidence=0.82,
        )

    if _contains_any(text, ("skill", "skills", "competencia", "competencias", "habilidade", "habilidades", "mapear meus", "autoavaliacao")):
        return JourneySignal(
            track=TRACK_SKILLS,
            intent="map_skills",
            goal=_safe_public_text(raw),
            focus_area="skills",
            confidence=0.84,
        )

    if _contains_any(text, ("lideranca", "liderar", "comunicacao", "comunicar", "gestao de pessoas", "influencia")):
        return JourneySignal(
            track=TRACK_LEADERSHIP,
            intent="develop_leadership",
            goal=_safe_public_text(raw),
            focus_area="leadership",
            confidence=0.80,
        )

    if _contains_any(text, ("desenvolver", "desenvolvimento", "carreira", "crescer profissional", "evoluir profissional", "mentoria")):
        return JourneySignal(
            track=TRACK_DEVELOPMENT,
            intent="professional_development",
            goal=_safe_public_text(raw),
            focus_area="career",
            confidence=0.78,
        )

    if _contains_any(text, ("inteligencia artificial", "projeto de ia", "projeto ia", "uso de ia", "com ia", "automacao", "automatizar", "empresa", "processo")):
        return JourneySignal(
            track=TRACK_INNOVATION,
            intent="innovation_ai_project",
            goal=_safe_public_text(raw),
            focus_area="innovation_ai",
            confidence=0.80,
        )

    if _contains_any(text, ("novo negocio", "negocio", "empreender", "startup", "empresa nova", "criar uma empresa", "abrir empresa")):
        return JourneySignal(
            track=TRACK_ENTREPRENEURSHIP,
            intent="new_business",
            goal=_safe_public_text(raw),
            focus_area="entrepreneurship",
            confidence=0.79,
        )

    if _contains_any(text, ("diagnostico", "analisar minha empresa", "melhorar vendas", "margem", "operacao", "processo comercial")):
        return JourneySignal(
            track=TRACK_BUSINESS_DIAGNOSTIC,
            intent="business_diagnostic",
            goal=_safe_public_text(raw),
            focus_area="business",
            confidence=0.76,
        )

    if _contains_any(text, ("testar", "me conduza", "explorar", "o que posso fazer", "como usar", "patroai", "orkio")):
        return JourneySignal(
            track=TRACK_PLATFORM_EXPLORATION,
            intent="platform_exploration",
            goal=_safe_public_text(raw),
            focus_area="exploration",
            confidence=0.70,
        )

    return JourneySignal(
        track=TRACK_PLATFORM_EXPLORATION,
        intent="exploration",
        goal=_safe_public_text(raw),
        focus_area="exploration",
        confidence=0.55,
    )


def merge_journey_snapshot(
    previous: Optional[Dict[str, Any]],
    signal: JourneySignal | Dict[str, Any] | None,
    *,
    max_history: int = 8,
) -> Dict[str, Any]:
    """Atualiza snapshot público-seguro da jornada."""

    prev = deepcopy(previous or {})
    sig = signal.to_dict() if isinstance(signal, JourneySignal) else deepcopy(signal or {})
    now = int(time.time())

    current_track = str(sig.get("track") or prev.get("current_track") or TRACK_PLATFORM_EXPLORATION)
    track_meta = PUBLIC_JOURNEY_TRACKS.get(current_track, PUBLIC_JOURNEY_TRACKS[TRACK_PLATFORM_EXPLORATION])

    event = {
        "track": current_track,
        "intent": str(sig.get("intent") or "exploration"),
        "goal": _safe_public_text(sig.get("goal") or ""),
        "focus_area": _safe_public_text(sig.get("focus_area") or ""),
        "confidence": round(float(sig.get("confidence") or 0.55), 2),
        "at": int(sig.get("created_at") or now),
    }

    history = list(prev.get("history") or [])
    history.append(event)
    history = history[-max_history:]

    return {
        "version": JOURNEY_MEMORY_VERSION,
        "public_speaker": PUBLIC_SPEAKER,
        "current_track": current_track,
        "current_track_label": track_meta.get("label") or current_track,
        "last_intent": event["intent"],
        "last_goal": event["goal"],
        "last_focus_area": event["focus_area"],
        "recommended_next_question": track_meta.get("next_question") or "",
        "history": history,
        "updated_at": now,
    }


def build_journey_continuity_hint(snapshot: Optional[Dict[str, Any]]) -> str:
    """Gera hint curto para overlay futuro.

    Não deve ser exibido cru ao usuário sem passar pela síntese do Orkio.
    """

    data = snapshot if isinstance(snapshot, dict) else {}
    label = str(data.get("current_track_label") or "").strip()
    goal = _safe_public_text(data.get("last_goal") or "", limit=180)
    question = str(data.get("recommended_next_question") or "").strip()

    if not label:
        return ""

    if goal:
        return (
            f"Continuidade de jornada: na última interação pública-segura, o usuário explorava "
            f"{label}. Objetivo sinalizado: {goal}. Próxima pergunta útil: {question}"
        ).strip()

    return (
        f"Continuidade de jornada: o usuário explorava {label}. "
        f"Próxima pergunta útil: {question}"
    ).strip()


def build_public_memory_receipt(snapshot: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    data = snapshot if isinstance(snapshot, dict) else {}
    return {
        "version": JOURNEY_MEMORY_VERSION,
        "public_speaker": PUBLIC_SPEAKER,
        "track": data.get("current_track") or TRACK_PLATFORM_EXPLORATION,
        "track_label": data.get("current_track_label") or PUBLIC_JOURNEY_TRACKS[TRACK_PLATFORM_EXPLORATION]["label"],
        "updated_at": data.get("updated_at") or int(time.time()),
        "memory_scope": "public_journey",
    }

# ---------------------------------------------------------------------------
# AO67E compatibility layer
# Mantém compatibilidade com AO67B Orkio Decision Mesh após AO67D substituir
# journey_memory.py por uma versão persistente.
# ---------------------------------------------------------------------------

def _ao67e_safe_text(value: Any, limit: int = 500) -> str:
    text = str(value or "").strip()
    if len(text) > limit:
        return text[: max(0, limit - 3)].rstrip() + "..."
    return text


def build_journey_memory_snapshot(
    *,
    current_message: Any,
    previous_messages: Optional[Iterable[Any]] = None,
    prior_memory: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Snapshot compatível com AO67B e enriquecido por AO67D.

    Esta função não persiste em banco. Ela apenas cria um snapshot público-seguro
    em memória para o Decision Mesh. A persistência continua isolada em
    journey_memory_persistence.py / journey_memory_service.py.
    """

    signal = detect_journey_track(current_message)
    base_snapshot = merge_journey_snapshot(prior_memory or {}, signal)

    previous = list(previous_messages or [])
    previous_compact = [_ao67e_safe_text(item, 220) for item in previous[-6:]]

    recent_intents = []
    for item in list((prior_memory or {}).get("recent_intents") or []):
        if item and item not in recent_intents:
            recent_intents.append(str(item))
    if signal.intent and (not recent_intents or recent_intents[-1] != signal.intent):
        recent_intents.append(signal.intent)
    recent_intents = recent_intents[-8:]

    continuity_prompt = build_journey_continuity_hint(base_snapshot)

    enriched = dict(base_snapshot)
    enriched.update(
        {
            "ok": True,
            "service": "journey_memory",
            "version": JOURNEY_MEMORY_VERSION,
            "current_intent": signal.intent,
            "current_route_family": "public_journey",
            "current_confidence": round(float(signal.confidence or 0.0), 2),
            "recent_intents": recent_intents,
            "previous_messages_compact": previous_compact,
            "continuity_prompt": continuity_prompt,
            "visible_agent": PUBLIC_SPEAKER,
            "final_speaker": PUBLIC_SPEAKER,
            "public_speaker": PUBLIC_SPEAKER,
            "memory_scope": "public_journey",
            "persisted": False,
        }
    )
    return enriched


def journey_memory_runtime_hints(memory_snapshot: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Hints compactos para system_overlay/runtime_hints.

    Não expõe especialistas, bastidores ou dados sensíveis. Pode ser usado pelo
    Decision Mesh para dar continuidade de jornada ao Orkio.
    """

    snapshot = memory_snapshot if isinstance(memory_snapshot, dict) else {}
    return {
        "journey_memory": {
            "version": JOURNEY_MEMORY_VERSION,
            "public_speaker": PUBLIC_SPEAKER,
            "current_track": snapshot.get("current_track") or TRACK_PLATFORM_EXPLORATION,
            "current_track_label": snapshot.get("current_track_label") or PUBLIC_JOURNEY_TRACKS[TRACK_PLATFORM_EXPLORATION]["label"],
            "last_intent": snapshot.get("last_intent") or snapshot.get("current_intent") or "exploration",
            "continuity_hint": snapshot.get("continuity_prompt") or build_journey_continuity_hint(snapshot),
            "memory_scope": "public_journey",
            "specialists_visible": False,
        }
    }
