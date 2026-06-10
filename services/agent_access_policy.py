from __future__ import annotations

"""
AO67A — Agent Access Policy

Camada pequena e auditável para separar:
- conhecimento/capacidade interna do agente
- visibilidade pública do agente
- resposta segura na superfície pública

Esta política não executa agentes, não escreve no banco, não faz deploy e não
altera permissões reais. Ela apenas padroniza decisões de exposição pública.
"""

import re
import unicodedata
from typing import Any, Dict, Iterable, Optional


AGENT_ACCESS_POLICY_VERSION = "AO67A_AGENT_ACCESS_POLICY_V1"

PUBLIC_VISIBLE_AGENT_NAME = "Orkio"
PUBLIC_VISIBLE_AGENT_ID = "orkio"

_INTERNAL_AGENT_TOKENS = {
    "chris",
    "cris",
    "orion",
    "warren",
    "cfo",
    "cto",
    "coo",
    "auditor",
    "systems architect",
    "backend engineer",
    "frontend engineer",
    "qa release engineer",
    "devops sre",
    "security guardian",
    "data db architect",
    "realtime voice engineer",
}

_PUBLIC_AGENT_QUERY_MARKERS = {
    "agente",
    "agentes",
    "agente especializado",
    "agentes especializados",
    "especialista",
    "especialistas",
    "especializado",
    "especializados",
    "quais agentes",
    "que agentes",
    "existem na plataforma",
    "disponiveis",
    "disponíveis",
    "quem pode ajudar",
    "quem analisar",
}


def _strip_accents(value: Any) -> str:
    raw = str(value or "")
    try:
        normalized = unicodedata.normalize("NFD", raw)
        return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    except Exception:
        return raw


def normalize_agent_text(value: Any) -> str:
    raw = _strip_accents(value).lower()
    raw = re.sub(r"[^a-z0-9@:/\.\-_\s]+", " ", raw, flags=re.I)
    return re.sub(r"\s+", " ", raw).strip()


def contains_any_marker(text: str, markers: Iterable[str]) -> bool:
    haystack = normalize_agent_text(text)
    return any(normalize_agent_text(marker) in haystack for marker in markers if str(marker or "").strip())


def is_internal_agent_name(value: Any) -> bool:
    token = normalize_agent_text(value).lstrip("@")
    if not token:
        return False
    return token in _INTERNAL_AGENT_TOKENS


def message_mentions_internal_agent(value: Any) -> bool:
    text = normalize_agent_text(value)
    if not text:
        return False
    return any(
        re.search(rf"(^|[^a-z0-9_@])@?{re.escape(token)}(?=$|[^a-z0-9_])", text)
        for token in _INTERNAL_AGENT_TOKENS
        if token not in {"cfo", "cto", "coo"} or f" {token} " in f" {text} "
    )


def is_public_agent_catalog_question(value: Any, *args: Any, **kwargs: Any) -> bool:
    text = normalize_agent_text(value)
    if not text:
        return False

    has_agent_subject = contains_any_marker(text, _PUBLIC_AGENT_QUERY_MARKERS)
    has_catalog_action = contains_any_marker(
        text,
        (
            "quais",
            "que",
            "existem",
            "disponiveis",
            "disponíveis",
            "plataforma",
            "tem",
            "lista",
            "listar",
            "mostrar",
            "me mostra",
            "me diga",
            "quem",
        ),
    )
    return bool(has_agent_subject and has_catalog_action)


def is_public_internal_agent_request(value: Any, *args: Any, **kwargs: Any) -> bool:
    text = normalize_agent_text(value)
    if not text:
        return False

    if message_mentions_internal_agent(text):
        return True

    if is_public_agent_catalog_question(text):
        return True

    # Frases como "especialista financeiro", "especialista de tecnologia" e
    # "agentes especializados" são tratadas como catálogo/capacidade futura,
    # não como agentes disponíveis publicamente.
    return contains_any_marker(
        text,
        (
            "especialista financeiro",
            "especialista de tecnologia",
            "especialistas financeiros",
            "especialistas de tecnologia",
            "agentes especializados",
            "agente especializado",
            "agentes internos",
            "agente interno",
        ),
    )


def public_visible_agent_name(value: Any = None) -> str:
    """Na superfície pública, Orkio é o condutor visível."""
    return PUBLIC_VISIBLE_AGENT_NAME


def build_public_agent_access_decision(
    *,
    requested_agent: Any = None,
    message: Any = None,
    reason: str = "public_agent_access_policy",
) -> Dict[str, Any]:
    requested = str(requested_agent or "").strip()
    blocked = requested or ("internal_agent_or_specialist" if is_public_internal_agent_request(message) else "")

    return {
        "allowed": False,
        "reason": reason,
        "policy_version": AGENT_ACCESS_POLICY_VERSION,
        "requested_agent": requested or None,
        "blocked_agent": blocked or None,
        "resolved_agent": PUBLIC_VISIBLE_AGENT_NAME,
        "visible_agent": PUBLIC_VISIBLE_AGENT_NAME,
        "agent_name": PUBLIC_VISIBLE_AGENT_NAME,
        "agent_id": PUBLIC_VISIBLE_AGENT_ID,
        "write_executed": False,
        "proposal_created": False,
        "branch_created": False,
        "pr_created": False,
        "deploy_executed": False,
    }


def public_agent_catalog_answer(*args: Any, **kwargs: Any) -> str:
    return (
        "Neste beta público, o agente visível disponível é o Orkio, que conduz a experiência principal pelo chat.\n\n"
        "Agentes especializados e funcionalidades avançadas poderão ser liberados futuramente conforme a evolução das conversas, "
        "o uso correto da ferramenta e as necessidades identificadas. Por enquanto, eu posso conduzir sua análise diretamente "
        "por aqui, sem exigir que você escolha um agente.\n\n"
        "Você pode testar o Orkio em trilhas como desenvolvimento profissional, mapeamento de skills, networking, liderança, "
        "inovação na empresa, projetos de IA, diagnóstico de ideias ou criação de novos negócios."
    )


def public_agent_access_denied_answer(*args: Any, **kwargs: Any) -> str:
    return (
        "Neste beta público, a experiência é conduzida por mim, Orkio, como copiloto principal. "
        "Eu não aciono agentes internos ou especialistas por nome nesta etapa.\n\n"
        "Traga a necessidade em linguagem simples. Eu posso organizar contexto, objetivo, riscos, alternativas e próximos passos "
        "diretamente por aqui. Com a evolução das conversas, o uso correto da ferramenta e a identificação de necessidades "
        "específicas, novas funcionalidades e agentes especializados poderão ser liberados futuramente."
    )
