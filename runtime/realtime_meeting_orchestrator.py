# EFATA777_V8_REALTIME_MEETING_ORCHESTRATOR
# Structural minimum backend module for Realtime "room by turns".
#
# Goal:
# - Keep realtime routing out of main.py.
# - Detect spoken requests such as "Orion, chame a Chris" or "Chris, chama o Orion".
# - Return an explicit directive to the frontend so it can session.update + response.create
#   exactly once with the correct active speaker.
# - Do not pretend parallel multi-agent execution if it did not happen. This module
#   orchestrates turn-taking and meeting state; full parallel agents remain a later layer.

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class MeetingAgentProfile:
    slug: str
    display_name: str
    role_label: str
    description: str
    voice_hint: str = ""
    aliases: Tuple[str, ...] = ()


AGENTS: Dict[str, MeetingAgentProfile] = {
    "orkio": MeetingAgentProfile(
        slug="orkio",
        display_name="Orkio",
        role_label="copiloto executivo",
        description=(
            "copiloto executivo e facilitador principal da Patroai; organiza a conversa, "
            "mantém continuidade e faz handoff para agentes internos quando solicitado"
        ),
        aliases=("orkio", "orquio", "archio", "workio", "workq", "copiloto"),
    ),
    "team": MeetingAgentProfile(
        slug="team",
        display_name="Team",
        role_label="coordenação da sala",
        description=(
            "modo de coordenação executiva da equipe; organiza turnos, responsáveis, riscos "
            "e próximos passos sem sobreposição de fala"
        ),
        aliases=("team", "time", "equipe", "todos", "sala", "war room", "reuniao", "reunião"),
    ),
    "orion": MeetingAgentProfile(
        slug="orion",
        display_name="Orion",
        role_label="CTO técnico",
        description=(
            "agente técnico/CTO da Patroai; conduz diagnóstico de backend, frontend, realtime, "
            "logs, deploy, rollback, arquitetura e estabilidade"
        ),
        aliases=("orion", "oria", "orlan", "auria", "aurya", "arian", "aryan", "warren", "cto", "tecnico", "técnico", "diagnostico", "diagnóstico"),
    ),
    "chris": MeetingAgentProfile(
        slug="chris",
        display_name="Chris",
        role_label="financeiro e estratégia",
        description=(
            "agente financeiro e estratégico da Patroai; conduz valuation, captação, viabilidade, "
            "go-to-market, funil, pricing e análise de negócio"
        ),
        aliases=("chris", "cris", "criz", "crys", "crista", "cristo", "cruz", "c h r i s", "c-h-r-i-s", "cfo", "financeiro", "valuation", "captação", "captacao"),
    ),
}


ACTION_WORDS = (
    "chame", "chamar", "inclua", "incluir", "traga", "trazer", "aciona", "acionar",
    "passa", "passar", "assuma", "assumir", "entra", "entrar", "conversa",
    "falar", "fala", "quero falar", "volta", "retorna", "troca", "trocar",
    "peça", "peca", "pergunte", "consulte", "ouve", "escuta", "online",
)

AUDIT_WORDS = (
    "auditoria", "auditar", "read only", "readonly", "read-only", "war room",
    "orquestracao", "orquestração", "realtime", "real time", "logs", "diagnostico",
    "diagnóstico", "backend", "frontend", "runtime", "sistema", "estabilidade",
)


def _strip_accents(value: str) -> str:
    try:
        return "".join(ch for ch in unicodedata.normalize("NFD", value) if unicodedata.category(ch) != "Mn")
    except Exception:
        return value


def normalize_text(value: Any) -> str:
    raw = str(value or "").strip()
    raw = _strip_accents(raw).lower()
    raw = re.sub(r"[^a-z0-9@#\s\-]+", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def compact_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_text(value))


def _event_name(event: Any) -> str:
    if isinstance(event, dict):
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        meta = event.get("meta") if isinstance(event.get("meta"), dict) else {}
        return str(
            event.get("name")
            or event.get("event")
            or event.get("type")
            or payload.get("event_type")
            or meta.get("event_type")
            or ""
        ).strip()
    payload = getattr(event, "payload", None)
    payload = payload if isinstance(payload, dict) else {}
    meta = getattr(event, "meta", None)
    meta = meta if isinstance(meta, dict) else {}
    return str(
        getattr(event, "name", None)
        or getattr(event, "event", None)
        or getattr(event, "type", None)
        or payload.get("event_type")
        or meta.get("event_type")
        or ""
    ).strip()


def _event_text(event: Any) -> str:
    candidates: List[Any] = []
    if isinstance(event, dict):
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        meta = event.get("meta") if isinstance(event.get("meta"), dict) else {}
        candidates.extend([
            event.get("content"),
            event.get("text"),
            event.get("transcript"),
            event.get("transcript_raw"),
            event.get("transcript_punct"),
            payload.get("content"),
            payload.get("text"),
            payload.get("transcript"),
            meta.get("content"),
            meta.get("text"),
            meta.get("transcript"),
        ])
    else:
        payload = getattr(event, "payload", None)
        payload = payload if isinstance(payload, dict) else {}
        meta = getattr(event, "meta", None)
        meta = meta if isinstance(meta, dict) else {}
        candidates.extend([
            getattr(event, "content", None),
            getattr(event, "text", None),
            getattr(event, "transcript", None),
            getattr(event, "transcript_raw", None),
            getattr(event, "transcript_punct", None),
            payload.get("content"),
            payload.get("text"),
            payload.get("transcript"),
            meta.get("content"),
            meta.get("text"),
            meta.get("transcript"),
        ])

    for item in candidates:
        text = str(item or "").strip()
        if text:
            return text
    return ""


def latest_user_transcript(events: Iterable[Any]) -> str:
    latest = ""
    for ev in events or []:
        name = _event_name(ev).lower()
        if name != "transcript.final":
            continue
        text = _event_text(ev)
        if text:
            latest = text
    return latest


def detect_agent_slug(text: str) -> Optional[str]:
    n = normalize_text(text)
    c = compact_text(text)
    if not n:
        return None

    # Specific agents first, to prevent "team/war room" from swallowing direct mentions.
    order = ("chris", "orion", "orkio", "team")
    for slug in order:
        profile = AGENTS[slug]
        for alias in profile.aliases:
            a = normalize_text(alias)
            ac = compact_text(alias)
            if not a:
                continue
            if re.search(rf"(^|\b){re.escape(a)}(\b|$)", n):
                return slug
            if ac and ac in c:
                return slug
    return None


def detect_direct_address(text: str) -> Optional[str]:
    n = normalize_text(text)
    if not n:
        return None

    for slug in ("chris", "orion", "orkio", "team"):
        for alias in AGENTS[slug].aliases:
            a = normalize_text(alias)
            if not a:
                continue
            if re.search(rf"^(oi|ola|olá|hey|fala|escuta|ouve)?\s*{re.escape(a)}(\b|,|!|\?)", n):
                return slug
            if re.search(rf"\b{re.escape(a)}\s*(ta|esta|está|online|me escuta|ouvindo|pode|por favor|assume|entra)\b", n):
                return slug
    return None


def has_action_intent(text: str) -> bool:
    n = normalize_text(text)
    return any(word in n for word in ACTION_WORDS)


def has_audit_intent(text: str) -> bool:
    n = normalize_text(text)
    return any(word in n for word in AUDIT_WORDS)


def detect_room_mode(text: str) -> bool:
    n = normalize_text(text)
    return bool(re.search(r"\b(sala|reuniao|war room|todos|equipe|time|a tres|a 3|conversa a tres|orquestr)\b", n))


def _agent_payload(slug: str) -> Dict[str, Any]:
    p = AGENTS.get(slug) or AGENTS["orkio"]
    return {
        "slug": p.slug,
        "display_name": p.display_name,
        "role_label": p.role_label,
        "description": p.description,
        "voice_hint": p.voice_hint,
    }


def _meeting_instructions(*, target_slug: str, current_slug: str, kind: str, transcript: str, room_mode: bool) -> str:
    target = AGENTS.get(target_slug) or AGENTS["orkio"]
    current = AGENTS.get(current_slug) or AGENTS["orkio"]
    participants = ", ".join(f"{p.display_name} ({p.role_label})" for p in AGENTS.values())

    return (
        "EFATA777_V8 — WAR ROOM / MEETING ORCHESTRATOR.\n"
        "Você está numa sala de reunião realtime por turnos da Patroai.\n"
        f"Participantes disponíveis: {participants}.\n"
        f"Agente ativo deste turno: {target.display_name} — {target.role_label}.\n"
        f"Agente anterior/host: {current.display_name} — {current.role_label}.\n"
        f"Tipo de turno: {kind}.\n"
        f"Modo sala: {'ativo' if room_mode else 'desligado'}.\n\n"
        "Regras obrigatórias:\n"
        "1. Fale APENAS como o agente ativo deste turno.\n"
        "2. Não diga que executou commit, deploy, push, PR, migração, auditoria real ou chamada externa se isso não ocorreu.\n"
        "3. Se o usuário pediu handoff, confirme de forma breve que o turno foi passado e responda como o agente solicitado.\n"
        "4. Se o usuário pediu que agentes conversem entre si, explique que a sala está operando por turnos coordenados, sem sobreposição de voz, e avance com o próximo turno útil.\n"
        "5. Se for auditoria/read-only, separe Fato confirmado, Hipótese provável, Ação recomendada, Validação pendente e Risco residual.\n"
        "6. Nunca volte a se identificar como Orkio quando o agente ativo for Orion ou Chris.\n\n"
        f"Última fala do usuário: {transcript.strip()[:1200]}"
    )


def build_meeting_directive(
    *,
    session_id: str,
    events: Iterable[Any],
    current_agent_slug: Optional[str] = None,
    dest_mode: Optional[str] = None,
    promotion: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    transcript = latest_user_transcript(events)
    if not transcript:
        return None

    current = normalize_text(current_agent_slug or "") or "orkio"
    if current not in AGENTS:
        current = detect_agent_slug(current) or "orkio"

    explicit_target = detect_direct_address(transcript) or detect_agent_slug(transcript)
    action = has_action_intent(transcript)
    room_mode = detect_room_mode(transcript) or normalize_text(dest_mode or "") == "team"
    audit = has_audit_intent(transcript)

    if not explicit_target and not action and not audit and not room_mode:
        return None

    target = explicit_target or ("orion" if audit else current)
    if target not in AGENTS:
        target = "orkio"

    if audit:
        # Technical/audit requests should be owned by Orion unless user explicitly asked Chris.
        if target not in {"chris"}:
            target = "orion"

    kind = "addressed_turn"
    if target != current:
        kind = "handoff"
    if room_mode and target == "team":
        kind = "meeting_coordination"
    if audit:
        kind = "readonly_audit"
    if action and target != current:
        kind = "handoff"

    directive = {
        "status": "directive",
        "patch": "EFATA777_V8",
        "session_id": session_id,
        "thread_id": (promotion or {}).get("thread_id"),
        "kind": kind,
        "room_mode": bool(room_mode),
        "transcript": transcript,
        "current_agent": _agent_payload(current),
        "target_agent": _agent_payload(target),
        "target_agent_slug": target,
        "active_agent_slug": target,
        "should_create_response": True,
        "client_controlled_response": True,
        "dedupe_key": f"{session_id}:{kind}:{target}:{compact_text(transcript)[:180]}",
        "instructions": _meeting_instructions(
            target_slug=target,
            current_slug=current,
            kind=kind,
            transcript=transcript,
            room_mode=room_mode,
        ),
        "room_turns": [],
        "truthful_status": (
            "turn_routed" if target == current else "handoff_routed"
        ),
    }

    if room_mode or audit:
        directive["room_turns"] = [
            _agent_payload("orion"),
            _agent_payload("chris"),
            _agent_payload("orkio"),
        ]

    return directive


def summarize_directive_for_log(directive: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not directive:
        return {"status": "none"}
    return {
        "status": directive.get("status"),
        "kind": directive.get("kind"),
        "target": directive.get("target_agent_slug"),
        "room_mode": directive.get("room_mode"),
        "dedupe_key": directive.get("dedupe_key"),
    }
