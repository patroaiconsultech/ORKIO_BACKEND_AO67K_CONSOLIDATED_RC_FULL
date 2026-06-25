# PATCH_23_AGENT_REGISTRY_CANONICO
# PATCH_28_PERSONA_ISOLATION_AND_REGISTRY_DRIVEN_TEAM_PANEL
# Canonical backend registry for agent slugs, aliases, routing metadata and persona isolation.
#
# This module is dependency-free by design. It is safe to import from main.py,
# routes/realtime.py, runtime/turn_router.py and runtime/realtime_meeting_orchestrator.py
# without DB access or application startup side effects.

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple


AGENT_REGISTRY_VERSION = "PATCH_31_AGENT_REGISTRY_VOICE_PROFILE_V1"
AGENT_VOICE_PROFILE_VERSION = "PATCH_31_CANONICAL_AGENT_VOICE_PROFILE_V1"
AGENT_VOICE_PROFILE_PAYLOAD_VERSION = "PATCH_31_FINAL_CANONICAL_VOICE_PROFILE_PAYLOAD_V1"
AGENT_VOICE_PRECEDENCE_VERSION = "PATCH_31_FINAL_CANONICAL_VOICE_PRECEDENCE_V1"
AGENT_REALTIME_CONTRACT_VERSION = "PATCH_31_FINAL_PREMIUM_REALTIME_PERSONA_VOICE_CONTRACT_V1"
AGENT_VOICE_OVERRIDE_POLICY = "db_voice_requires_explicit_override_flag_and_never_overrides_env_or_registry"


@dataclass(frozen=True)
class CanonicalAgentProfile:
    slug: str
    display_name: str
    role_label: str
    description: str
    route_role: str = "specialist"
    public_beta_allowed: bool = False
    internal: bool = True
    # PATCH_28: explicit registry-driven policy fields. The older fields above
    # remain for compatibility; these fields are the canonical policy terms used
    # by Team Panel and Persona Isolation.
    public_agent: bool = False
    internal_agent: bool = True
    team_default: bool = False
    team_optional: bool = True
    voice_hint: str = ""
    voice_profile: str = ""
    voice_id: str = ""
    voice_env_key: str = ""
    voice_provider: str = "openai_realtime"
    aliases: Tuple[str, ...] = ()
    domain_keywords: Tuple[str, ...] = ()
    realtime_role_line: str = ""
    persona_scope: str = ""
    persona_guardrails: Tuple[str, ...] = ()


CANONICAL_AGENT_REGISTRY: Dict[str, CanonicalAgentProfile] = {
    "orkio": CanonicalAgentProfile(
        slug="orkio",
        display_name="Orkio",
        role_label="Copiloto executivo",
        description="copiloto executivo e facilitador principal da Patroai; organiza contexto, continuidade e próximos passos",
        route_role="host",
        public_beta_allowed=True,
        internal=False,
        public_agent=True,
        internal_agent=False,
        team_default=True,
        team_optional=False,
        voice_profile="orkio",
        voice_id="cedar",
        voice_env_key="VITE_ORKIO_VOICE_ID",
        voice_hint="Orkio — voz oficial",
        aliases=("orkio", "orquio", "archio", "workio", "workq"),
        domain_keywords=("copiloto", "patroai", "contexto", "continuidade", "estrategia", "estratégia"),
        realtime_role_line="Você é Orkio, agente executivo principal da plataforma Patroai.",
        persona_scope="Orkio organiza a sala, sintetiza contexto, prioriza próximos passos e preserva continuidade operacional.",
        persona_guardrails=(
            "Não assuma a identidade de Orion, Chris, Laura ou Auditor quando outro agente for o speaker ativo.",
            "Quando outro agente for chamado diretamente, não aja como intermediário visível.",
        ),
    ),
    "team": CanonicalAgentProfile(
        slug="team",
        display_name="Team",
        role_label="Sala executiva",
        description="modo de coordenação executiva da equipe; organiza turnos, responsáveis, riscos e próximos passos sem sobreposição de fala",
        route_role="room",
        public_beta_allowed=True,
        internal=False,
        public_agent=True,
        internal_agent=False,
        team_default=False,
        team_optional=False,
        voice_profile="team",
        voice_id="cedar",
        voice_env_key="VITE_TEAM_VOICE_ID",
        voice_hint="Team — coordenação",
        aliases=("team", "time", "equipe", "todos", "sala", "war room", "warroom", "squad"),
        domain_keywords=("reuniao", "reunião", "sala executiva", "painel", "mesa", "orquestracao", "orquestração"),
        realtime_role_line="Você está no modo Team, atuando como coordenador de sala executiva multiagente da Patroai.",
        persona_scope="Team é a sala, não um agente especialista; ele coordena turnos e painéis de resposta.",
        persona_guardrails=(
            "Não trate Team como speaker especializado quando houver agente ativo definido.",
            "Use o Team apenas para coordenação da sala e resposta em painel.",
        ),
    ),
    "orion": CanonicalAgentProfile(
        slug="orion",
        display_name="Orion",
        role_label="CTO técnico",
        description="agente técnico/CTO da Patroai; conduz diagnóstico de backend, frontend, realtime, logs, deploy, rollback, arquitetura e estabilidade",
        route_role="specialist",
        public_beta_allowed=False,
        internal=True,
        public_agent=False,
        internal_agent=True,
        team_default=True,
        team_optional=True,
        voice_profile="orion",
        voice_id="echo",
        voice_env_key="VITE_ORION_VOICE_ID",
        voice_hint="Orion — CTO técnico",
        aliases=("orion", "oria", "orlan", "auria", "aurya", "arian", "aryan", "warren", "cto"),
        domain_keywords=("tecnico", "técnico", "technical", "diagnostico", "diagnóstico", "arquitetura", "arquiteto", "devops", "backend", "frontend", "logs", "deploy", "rollback", "realtime", "build", "bug", "erro"),
        realtime_role_line="Você é Orion, agente interno CTO técnico da Patroai, responsável por diagnóstico técnico, arquitetura, bugs, logs, deploy, realtime e orquestração.",
        persona_scope="Orion responde como CTO técnico: arquitetura, código, bugs, logs, realtime, deploy, rollback, estabilidade e validação.",
        persona_guardrails=(
            "Não responda como Orkio, Chris, Laura ou Auditor.",
            "Separe fato confirmado, hipótese provável, patch sugerido, validação pendente e risco residual quando analisar problemas técnicos.",
            "Não declare deploy, commit, push, PR, migration ou validação real sem evidência.",
        ),
    ),
    "chris": CanonicalAgentProfile(
        slug="chris",
        display_name="Chris",
        role_label="Financeiro e estratégia",
        description="agente financeiro e estratégico da Patroai; conduz valuation, captação, viabilidade, go-to-market, funil, pricing e análise de negócio",
        route_role="specialist",
        public_beta_allowed=False,
        internal=True,
        public_agent=False,
        internal_agent=True,
        team_default=True,
        team_optional=True,
        voice_profile="chris",
        voice_id="coral",
        voice_env_key="VITE_CHRIS_VOICE_ID",
        voice_hint="Chris — financeiro e estratégia",
        aliases=("chris", "cris", "criz", "crys", "c h r i s", "c-h-r-i-s", "cfo"),
        domain_keywords=("financeiro", "financial", "comercial", "vendas", "valuation", "captação", "captacao", "pricing", "go-to-market", "receita", "funil"),
        realtime_role_line="Você é Chris, agente interno financeiro/estratégico da Patroai, responsável por análise financeira, precificação, viabilidade, riscos comerciais e estratégia de receita.",
        persona_scope="Chris responde pela ótica financeira, comercial, estratégica, de receita, valuation, captação e viabilidade.",
        persona_guardrails=(
            "Não responda como Orion em diagnóstico técnico profundo.",
            "Não responda como Laura em narrativa institucional quando a demanda for storytelling ou pitch.",
            "Não prometa captação, investimento ou resultado financeiro garantido.",
        ),
    ),
    "laura": CanonicalAgentProfile(
        slug="laura",
        display_name="Laura",
        role_label="Narrativa e investidores",
        description="agente de narrativa, business plan, pitch, investidores e storytelling institucional da Patroai",
        route_role="specialist",
        public_beta_allowed=False,
        internal=True,
        public_agent=False,
        internal_agent=True,
        team_default=True,
        team_optional=True,
        voice_profile="laura",
        voice_id="shimmer",
        voice_env_key="VITE_LAURA_VOICE_ID",
        voice_hint="Laura — narrativa e investidores",
        aliases=("laura",),
        domain_keywords=("investidor", "investidores", "pitch", "business plan", "narrativa", "storytelling", "deck", "plano de negocios", "plano de negócios", "sumario executivo", "sumário executivo"),
        realtime_role_line="Você é Laura, agente interno de narrativa, business plan e investidores da Patroai, responsável por clareza estratégica, pitch e storytelling executivo.",
        persona_scope="Laura responde pela ótica de narrativa, investidores, pitch, business plan, clareza institucional e storytelling executivo.",
        persona_guardrails=(
            "Não responda como Orion em execução técnica.",
            "Não invente dados de mercado, valuation ou métricas sem fonte ou evidência.",
            "Quando a informação for proposta narrativa, marque como proposta e não como fato comprovado.",
        ),
    ),
    "auditor": CanonicalAgentProfile(
        slug="auditor",
        display_name="Auditor",
        role_label="Auditoria externa",
        description="agente/função de auditoria externa e red-team; revisa riscos, evidências, validação e GO/NO-GO",
        route_role="specialist",
        public_beta_allowed=False,
        internal=True,
        public_agent=False,
        internal_agent=True,
        team_default=False,
        team_optional=True,
        voice_profile="auditor",
        voice_id="ash",
        voice_env_key="VITE_AUDITOR_VOICE_ID",
        voice_hint="Auditor — revisão crítica",
        aliases=("auditor", "auditor externo", "ao-01", "ao01"),
        domain_keywords=("auditoria", "red team", "red-team", "riscos", "validacao", "validação", "go/no-go"),
        realtime_role_line="Você é Auditor, agente/função de auditoria externa, responsável por revisão crítica, evidências, riscos e vereditos GO/NO-GO.",
        persona_scope="Auditor responde como revisão externa/read-only: evidências, riscos, validação, rollback e GO/NO-GO.",
        persona_guardrails=(
            "Não trate proposta como validação.",
            "Não aprove produção sem evidências de build, staging e teste end-to-end quando aplicável.",
            "Separe achado documental de achado prático.",
        ),
    ),
}


def _strip_accents(value: str) -> str:
    try:
        return "".join(ch for ch in unicodedata.normalize("NFD", value) if unicodedata.category(ch) != "Mn")
    except Exception:
        return value


def normalize_agent_lookup_value(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return ""
    raw = raw.lstrip("@")
    raw = _strip_accents(raw)
    raw = raw.replace("“", " ").replace("”", " ").replace('"', " ").replace("'", " ")
    raw = re.sub(r"[\s\-/]+", "_", raw)
    raw = re.sub(r"[^a-z0-9_]+", "", raw)
    raw = re.sub(r"_+", "_", raw).strip("_")
    return raw


def normalize_agent_text(value: Any) -> str:
    raw = str(value or "").strip().lower()
    raw = _strip_accents(raw)
    raw = raw.replace("“", " ").replace("”", " ").replace('"', " ").replace("'", " ")
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def _compact(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize_agent_lookup_value(value))


def _alias_matches(alias: Any, value: Any) -> bool:
    a = normalize_agent_lookup_value(alias)
    v = normalize_agent_lookup_value(value)
    if not a or not v:
        return False
    if a == v:
        return True
    ac = _compact(a)
    vc = _compact(v)
    return bool(ac and vc and (ac == vc or ac in vc))


def canonical_agent_profile(value: Any) -> Optional[CanonicalAgentProfile]:
    raw = normalize_agent_lookup_value(value)
    if not raw:
        return None
    direct = CANONICAL_AGENT_REGISTRY.get(raw)
    if direct:
        return direct
    for profile in CANONICAL_AGENT_REGISTRY.values():
        candidates: Tuple[Any, ...] = (profile.slug, profile.display_name, *profile.aliases)
        if any(_alias_matches(candidate, raw) for candidate in candidates):
            return profile
    return None


def canonical_agent_slug(value: Any, default: Optional[str] = "", *, allow_unknown: bool = False) -> Optional[str]:
    profile = canonical_agent_profile(value)
    if profile:
        return profile.slug
    if allow_unknown:
        normalized = normalize_agent_lookup_value(value)
        return normalized or default
    return default


def agent_display_name(slug_or_alias: Any, default: str = "Orkio") -> str:
    profile = canonical_agent_profile(slug_or_alias)
    if profile:
        return profile.display_name
    normalized = normalize_agent_lookup_value(slug_or_alias)
    if not normalized:
        return default
    return " ".join(part.capitalize() for part in normalized.split("_") if part) or default


def agent_aliases(slug_or_alias: Any) -> List[str]:
    profile = canonical_agent_profile(slug_or_alias)
    if not profile:
        return []
    seen: set[str] = set()
    out: List[str] = []
    for item in (profile.slug, profile.display_name, *profile.aliases):
        raw = str(item or "").strip()
        key = normalize_agent_lookup_value(raw)
        if raw and key not in seen:
            seen.add(key)
            out.append(raw)
    return out


def ordered_registry_slugs(include_internal: bool = True) -> List[str]:
    preferred = ["orkio", "team", "orion", "chris", "laura", "auditor"]
    out: List[str] = []
    for slug in preferred:
        profile = CANONICAL_AGENT_REGISTRY.get(slug)
        if profile and (include_internal or not profile.internal_agent):
            out.append(slug)
    for slug, profile in CANONICAL_AGENT_REGISTRY.items():
        if slug not in out and (include_internal or not profile.internal_agent):
            out.append(slug)
    return out


def team_default_member_slugs(include_internal: bool = True) -> List[str]:
    """Registry-driven Team Panel members.

    PATCH_28: this is the canonical source for generic "Equipe/Team" panels.
    Adding/removing a default panel member must be done in the registry profile,
    not inside the router or tests.
    """
    out: List[str] = []
    for slug in ordered_registry_slugs(include_internal=include_internal):
        profile = CANONICAL_AGENT_REGISTRY.get(slug)
        if not profile:
            continue
        if slug == "team":
            continue
        if not profile.team_default:
            continue
        if not include_internal and profile.internal_agent:
            continue
        out.append(slug)
    return out


def team_optional_member_slugs(include_internal: bool = True) -> List[str]:
    out: List[str] = []
    for slug in ordered_registry_slugs(include_internal=include_internal):
        profile = CANONICAL_AGENT_REGISTRY.get(slug)
        if not profile:
            continue
        if slug == "team":
            continue
        if not profile.team_optional:
            continue
        if not include_internal and profile.internal_agent:
            continue
        out.append(slug)
    return out


def is_public_agent(slug_or_alias: Any) -> bool:
    profile = canonical_agent_profile(slug_or_alias)
    return bool(profile and profile.public_agent)


def is_internal_agent(slug_or_alias: Any) -> bool:
    profile = canonical_agent_profile(slug_or_alias)
    return bool(profile.internal_agent) if profile else True


def persona_contract(slug_or_alias: Any) -> Dict[str, Any]:
    profile = canonical_agent_profile(slug_or_alias)
    if not profile:
        return {
            "slug": None,
            "display_name": "",
            "role_label": "",
            "persona_scope": "",
            "persona_guardrails": [],
            "realtime_role_line": "",
            "voice_profile": None,
            "voice_id": "",
            "voice_env_key": "",
            "voice_provider": "openai_realtime",
        }
    return {
        "slug": profile.slug,
        "display_name": profile.display_name,
        "role_label": profile.role_label,
        "persona_scope": profile.persona_scope or profile.description,
        "persona_guardrails": list(profile.persona_guardrails),
        "realtime_role_line": profile.realtime_role_line,
        "voice_profile": profile.voice_profile or profile.slug,
        "voice_id": profile.voice_id,
        "voice_env_key": profile.voice_env_key,
        "voice_provider": profile.voice_provider,
    }


def _voice_profile_payload(profile: CanonicalAgentProfile) -> Dict[str, Any]:
    """Canonical voice profile object exposed by the registry payload.

    PATCH_31_REV_A keeps legacy flat fields for compatibility, but the canonical
    contract is this object. Frontend should resolve provider voice from this
    registry/env profile first; DB/API voice fields are explicit overrides only.
    """
    return {
        "version": AGENT_VOICE_PROFILE_VERSION,
        "payload_version": AGENT_VOICE_PROFILE_PAYLOAD_VERSION,
        "precedence_version": AGENT_VOICE_PRECEDENCE_VERSION,
        "contract_version": AGENT_REALTIME_CONTRACT_VERSION,
        "override_policy": AGENT_VOICE_OVERRIDE_POLICY,
        "precedence": ["env", "registry", "db_override", "fallback"],
        "slug": profile.slug,
        "display_name": profile.display_name,
        "profile_id": profile.voice_profile or profile.slug,
        "voice_id": profile.voice_id or "cedar",
        "env_key": profile.voice_env_key or "",
        "provider": profile.voice_provider or "openai_realtime",
        "label": profile.voice_hint or profile.display_name,
        "source": "registry",
    }


def _profile_to_payload(profile: CanonicalAgentProfile) -> Dict[str, Any]:
    canonical_voice_profile = _voice_profile_payload(profile)
    return {
        "slug": profile.slug,
        "display_name": profile.display_name,
        "role_label": profile.role_label,
        "description": profile.description,
        "route_role": profile.route_role,
        "public_beta_allowed": bool(profile.public_beta_allowed),
        "internal": bool(profile.internal),
        "public_agent": bool(profile.public_agent),
        "internal_agent": bool(profile.internal_agent),
        "team_default": bool(profile.team_default),
        "team_optional": bool(profile.team_optional),
        "aliases": list(profile.aliases),
        "domain_keywords": list(profile.domain_keywords),
        "voice_hint": profile.voice_hint,
        # PATCH_31_REV_A: canonical voice profile object. Legacy consumers can use
        # voice_profile_id and the flat voice_* fields below.
        "voice_profile": canonical_voice_profile,
        "canonical_voice_profile": canonical_voice_profile,
        "voice_profile_id": profile.voice_profile or profile.slug,
        "voice_id": profile.voice_id,
        "voice_env_key": profile.voice_env_key,
        "voice_provider": profile.voice_provider,
        "voice_profile_version": AGENT_VOICE_PROFILE_VERSION,
        "voice_profile_payload_version": AGENT_VOICE_PROFILE_PAYLOAD_VERSION,
        "voice_precedence_version": AGENT_VOICE_PRECEDENCE_VERSION,
        "realtime_contract_version": AGENT_REALTIME_CONTRACT_VERSION,
        "voice_override_policy": AGENT_VOICE_OVERRIDE_POLICY,
        "persona_scope": profile.persona_scope,
        "persona_guardrails": list(profile.persona_guardrails),
    }


def registry_payload(include_internal: bool = True) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    for slug in ordered_registry_slugs(include_internal=include_internal):
        profile = CANONICAL_AGENT_REGISTRY[slug]
        items.append(_profile_to_payload(profile))
    return {
        "version": AGENT_REGISTRY_VERSION,
        "voice_profile_version": AGENT_VOICE_PROFILE_VERSION,
        "voice_profile_payload_version": AGENT_VOICE_PROFILE_PAYLOAD_VERSION,
        "voice_precedence_version": AGENT_VOICE_PRECEDENCE_VERSION,
        "realtime_contract_version": AGENT_REALTIME_CONTRACT_VERSION,
        "voice_override_policy": AGENT_VOICE_OVERRIDE_POLICY,
        "source": "canonical_static_v1",
        "count": len(items),
        "team_default_members": team_default_member_slugs(include_internal=include_internal),
        "team_optional_members": team_optional_member_slugs(include_internal=include_internal),
        "items": items,
    }


def enrich_catalog_item(item: Dict[str, Any], *, include_aliases: bool = True) -> Dict[str, Any]:
    data = dict(item or {})
    slug = canonical_agent_slug(data.get("slug") or data.get("name") or data.get("id"), default=None)
    if not slug:
        slug = canonical_agent_slug(data.get("agent_slug") or data.get("key") or data.get("code"), default=None)
    if not slug:
        return data

    profile = CANONICAL_AGENT_REGISTRY.get(slug)
    data["slug"] = slug
    if profile:
        data.setdefault("name", profile.display_name)
        data.setdefault("display_name", profile.display_name)
        data.setdefault("role", profile.role_label)
        data.setdefault("role_label", profile.role_label)
        data.setdefault("description", profile.description)
        data.setdefault("route_role", profile.route_role)
        data.setdefault("public_beta_allowed", bool(profile.public_beta_allowed))
        data.setdefault("internal", bool(profile.internal))
        data.setdefault("public_agent", bool(profile.public_agent))
        data.setdefault("internal_agent", bool(profile.internal_agent))
        data.setdefault("team_default", bool(profile.team_default))
        data.setdefault("team_optional", bool(profile.team_optional))
        data.setdefault("persona_scope", profile.persona_scope)
        data.setdefault("persona_guardrails", list(profile.persona_guardrails))
        data.setdefault("voice_hint", profile.voice_hint)
        data.setdefault("voice_profile", profile.voice_profile or profile.slug)
        data.setdefault("canonical_voice_profile", _voice_profile_payload(profile))
        data.setdefault("voice_profile_id", profile.voice_profile or profile.slug)
        data.setdefault("voice_id", profile.voice_id)
        data.setdefault("voice_env_key", profile.voice_env_key)
        data.setdefault("voice_provider", profile.voice_provider)
        data.setdefault("voice_profile_version", AGENT_VOICE_PROFILE_VERSION)
        data.setdefault("voice_profile_payload_version", AGENT_VOICE_PROFILE_PAYLOAD_VERSION)
        if include_aliases:
            data["aliases"] = agent_aliases(slug)
            data["domain_keywords"] = list(profile.domain_keywords)
        data["agent_registry_version"] = AGENT_REGISTRY_VERSION
    return data


def agent_voice_profile(slug_or_alias: Any, default_slug: str = "orkio") -> Dict[str, Any]:
    profile = canonical_agent_profile(slug_or_alias) or canonical_agent_profile(default_slug)
    if not profile:
        return {
            "version": AGENT_VOICE_PROFILE_VERSION,
            "payload_version": AGENT_VOICE_PROFILE_PAYLOAD_VERSION,
            "slug": default_slug,
            "display_name": "",
            "profile_id": default_slug,
            "voice_id": "cedar",
            "env_key": "VITE_ORKIO_VOICE_ID",
            "provider": "openai_realtime",
            "label": "Orkio — voz oficial",
            "source": "fallback",
            "precedence_version": AGENT_VOICE_PRECEDENCE_VERSION,
            "contract_version": AGENT_REALTIME_CONTRACT_VERSION,
            "override_policy": AGENT_VOICE_OVERRIDE_POLICY,
            "precedence": ["env", "registry", "db_override", "fallback"],
        }
    data = _voice_profile_payload(profile)
    return data



def realtime_role_line(slug_or_alias: Any, default: str = "Você é Orkio, agente executivo principal da plataforma Patroai.") -> str:
    profile = canonical_agent_profile(slug_or_alias)
    if profile and profile.realtime_role_line:
        return profile.realtime_role_line
    return default
