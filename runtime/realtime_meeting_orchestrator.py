# EFATA777_V8_REALTIME_MEETING_ORCHESTRATOR
# PATCH_22_DIRECT_AGENT_ADDRESSING_IN_TEAM_MODE
# PATCH_23_AGENT_REGISTRY_CANONICO
# PATCH_24_TURN_ROUTER
# PATCH_24_REV_A_HANDOFF_COMMAND_PRECEDENCE
# PATCH_27_MULTI_AGENT_RESPONSE_CONTROL
# PATCH_28_PERSONA_ISOLATION_AND_REGISTRY_DRIVEN_TEAM_PANEL
# PATCH_29_OBSERVABILIDADE_E_LOGS
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

try:  # Runtime package import
    from app.runtime.agent_registry import (
        AGENT_REGISTRY_VERSION,
        agent_display_name as registry_agent_display_name,
        canonical_agent_slug as registry_canonical_agent_slug,
        ordered_registry_slugs as registry_ordered_slugs,
        registry_payload as build_agent_registry_payload,
        team_default_member_slugs as registry_team_default_slugs,
        persona_contract as registry_persona_contract,
    )
except Exception:  # pragma: no cover - local package fallback for tests
    from .agent_registry import (
        AGENT_REGISTRY_VERSION,
        agent_display_name as registry_agent_display_name,
        canonical_agent_slug as registry_canonical_agent_slug,
        ordered_registry_slugs as registry_ordered_slugs,
        registry_payload as build_agent_registry_payload,
        team_default_member_slugs as registry_team_default_slugs,
        persona_contract as registry_persona_contract,
    )

try:  # PATCH_24_TURN_ROUTER
# PATCH_24_REV_A_HANDOFF_COMMAND_PRECEDENCE
# PATCH_27_MULTI_AGENT_RESPONSE_CONTROL
# PATCH_28_PERSONA_ISOLATION_AND_REGISTRY_DRIVEN_TEAM_PANEL
# PATCH_29_OBSERVABILIDADE_E_LOGS
    from app.runtime.turn_router import (
        TURN_ROUTER_VERSION,
        classify_agent_turn,
        resolve_direct_agent_slug,
    )
except Exception:  # pragma: no cover - local package fallback for tests
    from .turn_router import (
        TURN_ROUTER_VERSION,
        classify_agent_turn,
        resolve_direct_agent_slug,
    )



@dataclass(frozen=True)
class MeetingAgentProfile:
    slug: str
    display_name: str
    role_label: str
    description: str
    voice_hint: str = ""
    aliases: Tuple[str, ...] = ()
    public_agent: bool = False
    internal_agent: bool = True
    team_default: bool = False
    team_optional: bool = True
    persona_scope: str = ""
    persona_guardrails: Tuple[str, ...] = ()


def _build_meeting_agents_from_registry() -> Dict[str, MeetingAgentProfile]:
    payload = build_agent_registry_payload(include_internal=True)
    items = payload.get("items") if isinstance(payload, dict) else []
    agents: Dict[str, MeetingAgentProfile] = {}
    for item in items or []:
        if not isinstance(item, dict):
            continue
        slug = str(item.get("slug") or "").strip().lower()
        if not slug:
            continue
        agents[slug] = MeetingAgentProfile(
            slug=slug,
            display_name=str(item.get("display_name") or registry_agent_display_name(slug, default=slug.title())),
            role_label=str(item.get("role_label") or "especialista"),
            description=str(item.get("description") or ""),
            voice_hint=str(item.get("voice_hint") or ""),
            aliases=tuple(str(alias) for alias in (item.get("aliases") or []) if str(alias or "").strip()),
            public_agent=bool(item.get("public_agent", item.get("public_beta_allowed", False))),
            internal_agent=bool(item.get("internal_agent", item.get("internal", True))),
            team_default=bool(item.get("team_default", False)),
            team_optional=bool(item.get("team_optional", True)),
            persona_scope=str(item.get("persona_scope") or item.get("description") or ""),
            persona_guardrails=tuple(str(rule) for rule in (item.get("persona_guardrails") or []) if str(rule or "").strip()),
        )
    return agents


AGENTS: Dict[str, MeetingAgentProfile] = _build_meeting_agents_from_registry()


ACTION_WORDS = (
    "chame", "chamar", "inclua", "incluir", "traga", "trazer", "aciona", "acionar",
    "passa", "passar", "assuma", "assumir", "entra", "entrar", "conversa",
    "falar", "fala", "quero falar", "volta", "retorna", "troca", "trocar",
    "peça", "peca", "pergunte", "pergunta", "consulte", "ouve", "ouvir", "quero ouvir",
    "gostaria de ouvir", "escuta", "online", "responda", "responder", "analise", "revise",
)

AUDIT_WORDS = (
    # PATCH_24_TURN_ROUTER:
    # Keep audit intent narrow. Domain words like "backend", "frontend" and
    # "logs" are now topic_classification signals, not automatic speaker handoffs.
    "auditoria", "auditar", "audite", "read only", "readonly", "read-only",
    "war room", "red team", "red-team", "go no-go", "go/no-go",
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


def _routing_detection_order() -> List[str]:
    # Specific speakers first; room/host fallbacks last.
    preferred = ["orion", "chris", "laura", "auditor", "orkio", "team"]
    ordered: List[str] = [slug for slug in preferred if slug in AGENTS]
    for slug in registry_ordered_slugs(include_internal=True):
        if slug in AGENTS and slug not in ordered:
            ordered.append(slug)
    return ordered


def detect_agent_slug(text: str) -> Optional[str]:
    # PATCH_24_TURN_ROUTER:
    # Backwards-compatible helper. It no longer treats every alias mention as a
    # routing command. Only direct_address/command_address returns a speaker.
    return resolve_direct_agent_slug(text, include_internal=True)


def detect_direct_address(text: str) -> Optional[str]:
    return resolve_direct_agent_slug(text, include_internal=True)


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
        "public_agent": bool(p.public_agent),
        "internal_agent": bool(p.internal_agent),
        "team_default": bool(p.team_default),
        "team_optional": bool(p.team_optional),
        "persona_scope": p.persona_scope,
        "persona_guardrails": list(p.persona_guardrails),
    }


def _meeting_instructions(
    *,
    target_slug: str,
    current_slug: str,
    kind: str,
    transcript: str,
    room_mode: bool,
    target_slugs: Optional[List[str]] = None,
    response_control: str = "",
) -> str:
    target = AGENTS.get(target_slug) or AGENTS["orkio"]
    current = AGENTS.get(current_slug) or AGENTS["orkio"]
    participants = ", ".join(f"{p.display_name} ({p.role_label})" for p in AGENTS.values())
    sequenced_targets = [
        (AGENTS.get(slug).display_name if AGENTS.get(slug) else str(slug).title())
        for slug in (target_slugs or [])
        if slug in AGENTS
    ]
    sequence_line = (
        f"Sequência solicitada: {' → '.join(sequenced_targets)}.\n"
        if len(sequenced_targets) > 1 else ""
    )
    response_control_line = (
        f"Controle de resposta: {response_control}.\n"
        if response_control else ""
    )
    persona = registry_persona_contract(target_slug)
    persona_scope = str(persona.get("persona_scope") or target.persona_scope or target.description or "").strip()
    persona_rules = [
        str(rule).strip()
        for rule in (persona.get("persona_guardrails") or target.persona_guardrails or [])
        if str(rule or "").strip()
    ]
    persona_line = f"Persona ativa: {persona_scope}.\n" if persona_scope else ""
    guardrail_line = (
        "Guardrails da persona ativa:\n"
        + "".join(f"- {rule}\n" for rule in persona_rules)
        if persona_rules else ""
    )

    return (
        "EFATA777_V8 — WAR ROOM / MEETING ORCHESTRATOR.\n"
        "Você está numa sala de reunião realtime por turnos da Patroai.\n"
        f"Participantes disponíveis: {participants}.\n"
        f"Agente ativo deste turno: {target.display_name} — {target.role_label}.\n"
        f"{persona_line}"
        f"{guardrail_line}"
        f"Agente anterior/host: {current.display_name} — {current.role_label}.\n"
        f"Tipo de turno: {kind}.\n"
        f"Modo sala: {'ativo' if room_mode else 'desligado'}.\n"
        f"{sequence_line}"
        f"{response_control_line}\n"
        "Regras obrigatórias:\n"
        "1. Fale APENAS como o agente ativo deste turno.\n"
        "2. Não diga que executou commit, deploy, push, PR, migração, auditoria real ou chamada externa se isso não ocorreu.\n"
        "3. Se o usuário chamou um agente pelo nome, responda diretamente como esse agente; não use Orkio como intermediário visível.\n"
        "4. Se o usuário pediu que agentes conversem entre si, explique que a sala está operando por turnos coordenados, sem sobreposição de voz, e avance com o próximo turno útil.\n"
        "5. Se for auditoria/read-only, separe Fato confirmado, Hipótese provável, Ação recomendada, Validação pendente e Risco residual.\n"
        "6. Nunca volte a se identificar como Orkio quando o agente ativo for Orion, Chris, Laura ou Auditor.\n"
        "7. Respeite o contrato de persona do registry; se a tarefa fugir da persona ativa, sinalize limite e sugira o agente adequado sem trocar de identidade sozinho.\n\n"
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

    current = registry_canonical_agent_slug(current_agent_slug or "", default="") or normalize_text(current_agent_slug or "") or "orkio"
    if current not in AGENTS:
        current = detect_agent_slug(current) or "orkio"

    turn = classify_agent_turn(transcript, include_internal=True)
    route_match_type = str(turn.get("match_type") or "")
    routed_match_types = {
        "direct_address",
        "command_address",
        "multi_agent_address",
        "multi_command_address",
        "team_panel",
    }
    target_slugs = [
        str(slug or "").strip().lower()
        for slug in (turn.get("target_agent_slugs") or [])
        if str(slug or "").strip()
    ]
    if not target_slugs and route_match_type in routed_match_types:
        one = str(turn.get("target_agent_slug") or "").strip().lower()
        if one:
            target_slugs = [one]
    target_slugs = [slug for slug in target_slugs if slug in AGENTS]
    direct_target = target_slugs[0] if target_slugs else None
    explicit_target = str(direct_target or "").strip().lower() or None
    multi_agent_turn = bool(turn.get("multi_agent_turn")) or len(target_slugs) > 1 or route_match_type == "team_panel"
    response_control = str(turn.get("response_control") or ("sequenced_team_turns" if multi_agent_turn else "")).strip()
    room_mode = detect_room_mode(transcript) or normalize_text(dest_mode or "") == "team" or multi_agent_turn
    audit = has_audit_intent(transcript)

    if not explicit_target and not audit and not room_mode:
        # Passive mentions and topic classification are diagnostic signals only
        # in PATCH 24/27. They must not trigger a speaker switch.
        return None

    target = explicit_target or ("orion" if audit else current)
    if target not in AGENTS:
        target = "orkio"

    if audit and not explicit_target:
        # Explicit audit/red-team commands are owned by Orion unless the user
        # directly addressed another available specialist.
        target = "orion"
        target_slugs = [target]

    kind = "addressed_turn"
    if target != current:
        kind = "handoff"
    if multi_agent_turn:
        kind = "multi_agent_sequence"
    if route_match_type == "team_panel":
        kind = "team_panel"
    if room_mode and target == "team":
        kind = "meeting_coordination"
    if audit:
        kind = "readonly_audit"
    if explicit_target and target != current and not multi_agent_turn:
        kind = "handoff"

    directive = {
        "status": "directive",
        "patch": "EFATA777_V12_PATCH29_MEETING_OBSERVABILITY",
        "agent_registry_version": AGENT_REGISTRY_VERSION,
        "turn_router_version": TURN_ROUTER_VERSION,
        "session_id": session_id,
        "thread_id": (promotion or {}).get("thread_id"),
        "kind": kind,
        "match_type": turn.get("match_type") or ("direct_address" if explicit_target else "implicit"),
        "turn_router": turn,
        "room_mode": bool(room_mode),
        "transcript": transcript,
        "current_agent": _agent_payload(current),
        "target_agent": _agent_payload(target),
        "target_agent_slug": target,
        "target_agent_slugs": target_slugs or [target],
        "active_agent_slug": target,
        # PATCH_29_OBSERVABILIDADE_E_LOGS:
        # Carry explicit transition metadata so routes/logs can explain why
        # a speaker/persona changed without parsing instructions.
        "speaker_transition": {
            "from_slug": current,
            "from_name": _agent_payload(current).get("display_name"),
            "to_slug": target,
            "to_name": _agent_payload(target).get("display_name"),
            "changed": bool(current != target),
        },
        "persona_transition": {
            "from_slug": registry_persona_contract(current).get("slug") or current,
            "to_slug": registry_persona_contract(target).get("slug") or target,
            "changed": bool((registry_persona_contract(current).get("slug") or current) != (registry_persona_contract(target).get("slug") or target)),
            "persona_version": AGENT_REGISTRY_VERSION,
        },
        "transition_reason": turn.get("match_type") or kind,
        "multi_agent_turn": bool(multi_agent_turn),
        "response_control": response_control or ("sequenced_team_turns" if multi_agent_turn else "single_turn"),
        "should_create_response": True,
        "client_controlled_response": True,
        "dedupe_key": f"{session_id}:{kind}:{'+'.join(target_slugs or [target])}:{compact_text(transcript)[:180]}",
        "instructions": _meeting_instructions(
            target_slug=target,
            current_slug=current,
            kind=kind,
            transcript=transcript,
            room_mode=room_mode,
            target_slugs=target_slugs or [target],
            response_control=response_control or ("sequenced_team_turns" if multi_agent_turn else ""),
        ),
        "room_turns": [],
        "truthful_status": (
            "turn_routed" if target == current else "handoff_routed"
        ),
    }

    if multi_agent_turn and target_slugs:
        directive["room_turns"] = [_agent_payload(slug) for slug in target_slugs if slug in AGENTS and slug != "team"]
        directive["sequence_remaining"] = [slug for slug in target_slugs[1:] if slug in AGENTS and slug != "team"]
    elif room_mode or audit:
        default_slugs = registry_team_default_slugs(include_internal=True)
        directive["room_turns"] = [
            _agent_payload(slug)
            for slug in default_slugs
            if slug in AGENTS and slug != "team"
        ]

    return directive


def summarize_directive_for_log(directive: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not directive:
        return {"status": "none"}
    target = directive.get("target_agent") if isinstance(directive.get("target_agent"), dict) else {}
    current = directive.get("current_agent") if isinstance(directive.get("current_agent"), dict) else {}
    return {
        "status": directive.get("status"),
        "kind": directive.get("kind"),
        "match_type": directive.get("match_type"),
        "transition_reason": directive.get("transition_reason") or directive.get("match_type") or directive.get("kind"),
        "target": directive.get("target_agent_slug"),
        "targets": directive.get("target_agent_slugs") or [],
        "speaker_transition": directive.get("speaker_transition") or {
            "from_slug": current.get("slug") or "",
            "to_slug": target.get("slug") or directive.get("target_agent_slug") or "",
            "changed": bool((current.get("slug") or "") != (target.get("slug") or directive.get("target_agent_slug") or "")),
        },
        "persona_transition": directive.get("persona_transition") or {
            "from_slug": current.get("slug") or "",
            "to_slug": target.get("slug") or directive.get("target_agent_slug") or "",
            "changed": bool((current.get("slug") or "") != (target.get("slug") or directive.get("target_agent_slug") or "")),
            "persona_version": directive.get("agent_registry_version") or AGENT_REGISTRY_VERSION,
        },
        "persona_version": directive.get("agent_registry_version") or AGENT_REGISTRY_VERSION,
        "multi_agent_turn": bool(directive.get("multi_agent_turn")),
        "response_control": directive.get("response_control"),
        "room_mode": directive.get("room_mode"),
        "dedupe_key": directive.get("dedupe_key"),
    }
