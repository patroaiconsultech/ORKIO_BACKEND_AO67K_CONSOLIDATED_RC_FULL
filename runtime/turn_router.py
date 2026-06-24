# PATCH_24_TURN_ROUTER
# Dependency-free turn classifier for the Patroai realtime meeting room.
#
# Purpose:
# - Separate direct agent addressing from passive mentions and topic keywords.
# - Prevent deterministic false positives such as:
#     "o backend precisa do CTO?" -> mention_reference, not direct_address
#     "preciso consultar o CFO?" -> mention_reference, not direct_address
#     "documento para Auditor?" -> mention_reference, not direct_address
# - Keep Direct Agent Addressing strict enough for Team Mode:
#     "CTO, revise" -> direct_address / orion
#     "chame o CTO" -> command_address / orion
#     "quero ouvir o CFO" -> command_address / chris
# - Add sequenced multi-agent routing:
#     "Orion e Chris, avaliem" -> multi_agent_address / [orion, chris]
#     "chame o CTO e o CFO" -> multi_command_address / [orion, chris]

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

try:  # Runtime package import
    from app.runtime.agent_registry import (
        AGENT_REGISTRY_VERSION,
        CANONICAL_AGENT_REGISTRY,
        agent_aliases,
        normalize_agent_text,
        ordered_registry_slugs,
        team_default_member_slugs,
    )
except Exception:  # pragma: no cover - local package fallback for tests
    from .agent_registry import (
        AGENT_REGISTRY_VERSION,
        CANONICAL_AGENT_REGISTRY,
        agent_aliases,
        normalize_agent_text,
        ordered_registry_slugs,
        team_default_member_slugs,
    )


TURN_ROUTER_VERSION = "PATCH_28_PERSONA_ISOLATION_TEAM_PANEL_V1"


def _alias_pattern(alias: Any) -> str:
    value = normalize_agent_text(alias)
    if not value:
        return ""
    # Allow spoken spacing/hyphenation for names like "c h r i s" and "c-h-r-i-s".
    escaped = re.escape(value)
    escaped = escaped.replace(r"\ ", r"\s*[- ]?\s*")
    return escaped


def _keyword_pattern(keyword: Any) -> str:
    value = normalize_agent_text(keyword)
    if not value:
        return ""
    return re.escape(value).replace(r"\ ", r"\s+")


def _profile_alias_pattern(slug: str) -> str:
    parts = [_alias_pattern(item) for item in agent_aliases(slug)]
    parts = [part for part in parts if part]
    return "|".join(parts)


def _profile_keyword_pattern(slug: str) -> str:
    profile = CANONICAL_AGENT_REGISTRY.get(slug)
    if not profile:
        return ""
    parts = [_keyword_pattern(item) for item in getattr(profile, "domain_keywords", ()) or ()]
    parts = [part for part in parts if part]
    return "|".join(parts)


def _profiles(include_internal: bool = True) -> List[str]:
    return ordered_registry_slugs(include_internal=include_internal)


def _empty_result() -> Dict[str, Any]:
    return {
        "match_type": "none",
        "target_agent_slug": None,
        "display_name": "",
        "confidence": 0.0,
        "registry_version": AGENT_REGISTRY_VERSION,
        "router_version": TURN_ROUTER_VERSION,
    }


def _profile_payload(slug: str, *, match_type: str, confidence: float, route_reason: str = "") -> Dict[str, Any]:
    profile = CANONICAL_AGENT_REGISTRY.get(slug)
    return {
        "slug": slug,
        "display_name": getattr(profile, "display_name", slug.title()) if profile else slug.title(),
        "match_type": match_type,
        "confidence": confidence,
        "route_reason": route_reason,
    }




def _command_pattern() -> str:
    command_phrases = (
        "chame", "chama", "chamar",
        "acione", "aciona", "acionar",
        "inclua", "inclui", "incluir",
        "traga", "traz", "trazer",
        "convoque", "convoca", "convocar",
        "quero ouvir", "gostaria de ouvir",
        "quero falar com", "fale com", "fala com",
        "pergunte para", "pergunta para", "pergunte ao", "pergunte a",
        "passa para", "passe para",
        "direciona para", "direcione para",
        "coloca", "coloque",
        "peça para", "peca para",
    )
    return "|".join(re.escape(item).replace(r"\ ", r"\s+") for item in command_phrases)


def _classify_command_for_slug(normalized: str, slug: str) -> Optional[Dict[str, Any]]:
    alias_pattern = _profile_alias_pattern(slug)
    if not alias_pattern:
        return None

    # PATCH_24_REV_A:
    # Handoff commands must beat an initial speaker vocative.
    # Example: "Orion, chame a Chris" must route to Chris, not Orion.
    # Passive references such as "o backend precisa do CTO?" remain mentions.
    command_pattern = _command_pattern()
    optional_article = r"(?:o|a|ao|pro|pra|para|para\s+o|para\s+a)?"

    command_address = re.compile(
        rf"(?:^|[\s,.:;!?—-])(?:por\s+favor\s+)?(?:{command_pattern})\s+{optional_article}\s*(?:@|#)?\s*(?:{alias_pattern})(?=$|\b|[\s,.:;!?—-])",
        re.IGNORECASE | re.UNICODE,
    )

    match = command_address.search(normalized)
    if not match:
        return None

    before_match = normalized[: match.start()].strip()
    if re.search(r"\b(?:nao|não)\s*$", before_match, re.IGNORECASE | re.UNICODE):
        return None

    return _profile_payload(
        slug,
        match_type="command_address",
        confidence=0.95 if match.start() > 0 else 0.94,
        route_reason="explicit_handoff_command_after_vocative" if match.start() > 0 else "explicit_routing_command",
    )

def _classify_direct_for_slug(normalized: str, slug: str) -> Optional[Dict[str, Any]]:
    alias_pattern = _profile_alias_pattern(slug)
    if not alias_pattern:
        return None

    greeting_words = (
        "oi", "ola", "olá", "hey", "bom dia", "boa tarde", "boa noite", "fala", "escuta", "ouve"
    )
    greeting_pattern = "|".join(re.escape(item).replace(r"\ ", r"\s+") for item in greeting_words)

    command_phrases = (
        "chame", "chama", "chamar",
        "acione", "aciona", "acionar",
        "inclua", "inclui", "incluir",
        "traga", "traz", "trazer",
        "convoque", "convoca", "convocar",
        "quero ouvir", "gostaria de ouvir",
        "quero falar com", "fale com", "fala com",
        "pergunte para", "pergunta para", "pergunte ao", "pergunte a",
        "passa para", "passe para",
        "direciona para", "direcione para",
        "coloca", "coloque",
        "peça para", "peca para",
    )
    command_pattern = "|".join(re.escape(item).replace(r"\ ", r"\s+") for item in command_phrases)
    optional_article = r"(?:o|a|ao|pro|pra|para|para\s+o|para\s+a)?"

    prefix_address = re.compile(
        rf"^\s*(?:@|#)?\s*(?:{alias_pattern})(?=$|[\s,.:;!?—-])",
        re.IGNORECASE | re.UNICODE,
    )
    greeting_address = re.compile(
        rf"^\s*(?:{greeting_pattern})\s+(?:@|#)?\s*(?:{alias_pattern})(?=$|[\s,.:;!?—-])",
        re.IGNORECASE | re.UNICODE,
    )
    command_address = re.compile(
        rf"^\s*(?:por\s+favor\s+)?(?:{command_pattern})\s+{optional_article}\s*(?:@|#)?\s*(?:{alias_pattern})(?=$|\b|[\s,.:;!?—-])",
        re.IGNORECASE | re.UNICODE,
    )

    if prefix_address.search(normalized):
        return _profile_payload(slug, match_type="direct_address", confidence=0.98, route_reason="alias_at_message_start")
    if greeting_address.search(normalized):
        return _profile_payload(slug, match_type="direct_address", confidence=0.96, route_reason="alias_after_greeting")
    if command_address.search(normalized):
        return _profile_payload(slug, match_type="command_address", confidence=0.94, route_reason="explicit_routing_command")
    return None


def _classify_mention_for_slug(normalized: str, slug: str) -> Optional[Dict[str, Any]]:
    alias_pattern = _profile_alias_pattern(slug)
    if not alias_pattern:
        return None
    mention = re.compile(
        rf"(?:^|\b)(?:{alias_pattern})(?=$|\b|[\s,.:;!?—-])",
        re.IGNORECASE | re.UNICODE,
    )
    if mention.search(normalized):
        return _profile_payload(slug, match_type="mention_reference", confidence=0.35)
    return None


def _classify_topic_for_slug(normalized: str, slug: str) -> Optional[Dict[str, Any]]:
    keyword_pattern = _profile_keyword_pattern(slug)
    if not keyword_pattern:
        return None
    topic = re.compile(
        rf"(?:^|\b)(?:{keyword_pattern})(?=$|\b|[\s,.:;!?—-])",
        re.IGNORECASE | re.UNICODE,
    )
    if topic.search(normalized):
        return _profile_payload(slug, match_type="topic_classification", confidence=0.25)
    return None



def _unique_slugs(values: List[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for value in values or []:
        slug = str(value or "").strip().lower()
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out.append(slug)
    return out


def _team_panel_slugs(include_internal: bool = True) -> List[str]:
    # PATCH_28_PERSONA_ISOLATION_AND_REGISTRY_DRIVEN_TEAM_PANEL:
    # Generic Team Panel membership is owned by the canonical registry through
    # profile.team_default. The router must not maintain a fixed participant list.
    return _unique_slugs(team_default_member_slugs(include_internal=include_internal))


def _slugs_mentioned_in_segment(segment: str, slugs: List[str]) -> List[str]:
    normalized = normalize_agent_text(segment)
    found: List[str] = []
    for slug in slugs:
        alias_pattern = _profile_alias_pattern(slug)
        if not alias_pattern:
            continue
        mention = re.compile(
            rf"(?:^|\b)(?:{alias_pattern})(?=$|\b|[\s,.:;!?—+\-])",
            re.IGNORECASE | re.UNICODE,
        )
        if mention.search(normalized):
            found.append(slug)
    return _unique_slugs(found)


def _payload_for_many(
    slugs: List[str],
    *,
    match_type: str,
    confidence: float,
    route_reason: str,
) -> Dict[str, Any]:
    clean = _unique_slugs(slugs)
    display_names: List[str] = []
    for slug in clean:
        profile = CANONICAL_AGENT_REGISTRY.get(slug)
        display_names.append(getattr(profile, "display_name", slug.title()) if profile else slug.title())
    first = clean[0] if clean else None
    return {
        "slug": first,
        "display_name": " + ".join(display_names),
        "display_names": display_names,
        "match_type": match_type,
        "confidence": confidence,
        "route_reason": route_reason,
        "target_agent_slug": first,
        "target_agent_slugs": clean,
        "multi_agent_turn": len(clean) > 1 or match_type == "team_panel",
        "response_control": "sequenced_team_turns",
    }


def _classify_team_panel(normalized: str, slugs: List[str]) -> Optional[Dict[str, Any]]:
    team_pattern = _profile_alias_pattern("team")
    if not team_pattern:
        return None

    # "Equipe, ..." / "Time, ..." / "Todos, ..." means the room should answer
    # as a coordinated panel. Passive phrases such as "o time comercial" should
    # not trigger this because we require the alias at the beginning.
    panel = re.compile(
        rf"^\s*(?:@|#)?\s*(?:{team_pattern})(?=$|[\s,.:;!?—-])",
        re.IGNORECASE | re.UNICODE,
    )
    if not panel.search(normalized):
        return None

    participants = _team_panel_slugs(include_internal=True)
    if not participants:
        return None
    return _payload_for_many(
        participants,
        match_type="team_panel",
        confidence=0.91,
        route_reason="team_alias_at_message_start",
    )


def _classify_multi_command(normalized: str, slugs: List[str]) -> Optional[Dict[str, Any]]:
    # Explicit routing command may request more than one speaker:
    # "chame o CTO e o CFO", "Orkio, quero ouvir Orion e Chris".
    command_pattern = _command_pattern()
    command = re.compile(
        rf"(?:^|[\s,.:;!?—-])(?:por\s+favor\s+)?(?:{command_pattern})\s+(?P<segment>[^.!?;\n]{{1,180}})",
        re.IGNORECASE | re.UNICODE,
    )
    match = command.search(normalized)
    if not match:
        return None

    before_match = normalized[: match.start()].strip()
    if re.search(r"\b(?:nao|não)\s*$", before_match, re.IGNORECASE | re.UNICODE):
        return None

    segment = match.group("segment") or ""
    found = _slugs_mentioned_in_segment(segment, slugs)
    found = [slug for slug in found if slug != "team"]
    if len(found) < 2:
        return None

    return _payload_for_many(
        found,
        match_type="multi_command_address",
        confidence=0.96,
        route_reason="explicit_multi_agent_handoff_command",
    )


def _classify_multi_direct(normalized: str, slugs: List[str]) -> Optional[Dict[str, Any]]:
    # Vocative group at the beginning:
    # "Orion e Chris, avaliem isso" / "CTO + CFO, revisem".
    prefix = re.match(r"^\s*(?P<segment>[^.!?;\n]{1,120}?)(?:[,:\u2014-]|\s+(?:por\s+favor|avaliem|respondam|revisem|analisem|analise|entrem|assumam|podem)\b)", normalized, re.IGNORECASE | re.UNICODE)
    if not prefix:
        return None

    segment = prefix.group("segment") or ""
    if not re.search(r"\b(?:e|com|junto|juntos|mais)\b|\+", segment, re.IGNORECASE | re.UNICODE):
        return None

    found = _slugs_mentioned_in_segment(segment, slugs)
    found = [slug for slug in found if slug != "team"]
    if len(found) < 2:
        return None

    # Prevent subject/reference questions from becoming a multi-agent route.
    # They do not start with an agent alias, while valid vocative groups do.
    starts_with_agent = any(_classify_direct_for_slug(normalized, slug) for slug in found)
    if not starts_with_agent:
        return None

    return _payload_for_many(
        found,
        match_type="multi_agent_address",
        confidence=0.94,
        route_reason="multi_agent_vocative_at_message_start",
    )


def classify_agent_turn(text: Any, *, include_internal: bool = True) -> Dict[str, Any]:
    raw = str(text or "").strip()
    if not raw:
        return _empty_result()

    normalized = normalize_agent_text(raw)
    if not normalized:
        return _empty_result()

    slugs = _profiles(include_internal=include_internal)

    # PATCH_27_MULTI_AGENT_RESPONSE_CONTROL:
    # Multi-agent/team commands are evaluated before single-agent routing so
    # "Orion e Chris, ..." does not collapse to only Orion.
    team_panel = _classify_team_panel(normalized, slugs)
    if team_panel:
        return {
            **team_panel,
            "registry_version": AGENT_REGISTRY_VERSION,
            "router_version": TURN_ROUTER_VERSION,
        }

    multi_command = _classify_multi_command(normalized, slugs)
    if multi_command:
        return {
            **multi_command,
            "registry_version": AGENT_REGISTRY_VERSION,
            "router_version": TURN_ROUTER_VERSION,
        }

    multi_direct = _classify_multi_direct(normalized, slugs)
    if multi_direct:
        return {
            **multi_direct,
            "registry_version": AGENT_REGISTRY_VERSION,
            "router_version": TURN_ROUTER_VERSION,
        }

    # PATCH_24_REV_A:
    # Explicit handoff commands must be evaluated before direct vocatives.
    # "Orion, chame a Chris" means Chris receives the turn; Orion is only
    # the addressed current speaker.
    for slug in slugs:
        command = _classify_command_for_slug(normalized, slug)
        if command:
            return {
                **command,
                "target_agent_slug": command["slug"],
                "registry_version": AGENT_REGISTRY_VERSION,
                "router_version": TURN_ROUTER_VERSION,
            }

    for slug in slugs:
        direct = _classify_direct_for_slug(normalized, slug)
        if direct:
            return {
                **direct,
                "target_agent_slug": direct["slug"],
                "registry_version": AGENT_REGISTRY_VERSION,
                "router_version": TURN_ROUTER_VERSION,
            }

    mentions: List[Dict[str, Any]] = []
    for slug in slugs:
        mention = _classify_mention_for_slug(normalized, slug)
        if mention:
            mentions.append(mention)
    if mentions:
        first = mentions[0]
        return {
            **first,
            "target_agent_slug": None,
            "mentioned_agent_slug": first["slug"],
            "mentioned_agents": [item["slug"] for item in mentions],
            "registry_version": AGENT_REGISTRY_VERSION,
            "router_version": TURN_ROUTER_VERSION,
        }

    topics: List[Dict[str, Any]] = []
    for slug in slugs:
        topic = _classify_topic_for_slug(normalized, slug)
        if topic:
            topics.append(topic)
    if topics:
        first = topics[0]
        return {
            **first,
            "target_agent_slug": None,
            "topic_agent_slug": first["slug"],
            "topic_agents": [item["slug"] for item in topics],
            "registry_version": AGENT_REGISTRY_VERSION,
            "router_version": TURN_ROUTER_VERSION,
        }

    return _empty_result()


def resolve_direct_agent_slug(text: Any, *, include_internal: bool = True) -> Optional[str]:
    classified = classify_agent_turn(text, include_internal=include_internal)
    if classified.get("match_type") in {"direct_address", "command_address", "multi_agent_address", "multi_command_address", "team_panel"}:
        slug = classified.get("target_agent_slug")
        return str(slug) if slug else None
    return None
