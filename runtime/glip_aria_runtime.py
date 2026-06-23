"""
AO-GLIP03 — Aria Runtime Persona Lock

Small, isolated runtime helper for GLIP / Aria mode.

Purpose:
- Keep app/main.py from growing even more.
- Detect GLIP/Arquitech/Aria requests from the frontend destination contract.
- Build a strict Aria system prompt.
- Clean legacy Orkio/PatroAI/AO audit leakage before it reaches the user.

This module has no database dependency and is safe to import from the chat runtime.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Optional


_ARCHITECTURE_KEYWORDS = (
    "arquitetura",
    "arquitetônico",
    "arquitetonica",
    "arquitetonico",
    "projeto",
    "obra",
    "briefing",
    "cliente",
    "proposta",
    "contrato",
    "cronograma",
    "fornecedor",
    "aprovação",
    "aprovacao",
    "documento",
    "documentação",
    "documentacao",
    "loja",
    "shopping",
    "clínica",
    "clinica",
    "consultório",
    "consultorio",
    "escritório",
    "escritorio",
    "interiores",
    "retrofit",
    "reforma",
    "margem",
    "escopo",
    "memorial",
)

_FORBIDDEN_LEAK_MARKERS = (
    "sou orkio",
    "patroai",
    "patroaí",
    "auditoria focada",
    "ao20bc",
    "router precedence",
    "technical_audit",
    "runtime distribuído",
    "runtime distribuido",
    "orquestração lógica",
    "orquestracao logica",
    "chris valuation",
    "orion",
    "team",
    "@orkio",
    "@chris",
    "@orion",
)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _slug(value: Any) -> str:
    raw = _clean(value).lower()
    raw = raw.replace("@", "")
    raw = re.sub(r"[^a-z0-9_\-À-ÿ]+", " ", raw, flags=re.IGNORECASE).strip()
    return raw


def _iter_names(values: Any) -> Iterable[str]:
    if values is None:
        return []
    if isinstance(values, (list, tuple, set)):
        return [_clean(v) for v in values if _clean(v)]
    return [_clean(values)]


def glip_aria_is_request(
    message: str = "",
    *,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
    requested_agent_names: Any = None,
    source: Any = None,
    product: Any = None,
    agent_id: Any = None,
    dest_mode: Any = None,
    route_plan: Optional[Dict[str, Any]] = None,
) -> bool:
    """Return True when the request belongs to the GLIP/Aria experience."""

    route_plan = route_plan if isinstance(route_plan, dict) else {}

    candidates = [
        visible_agent,
        target_agent_slug,
        source,
        product,
        agent_id,
        dest_mode,
        route_plan.get("visible_agent"),
        route_plan.get("target_agent_slug"),
        route_plan.get("source"),
        route_plan.get("product"),
        route_plan.get("requested_agent"),
        route_plan.get("resolved_agent"),
        route_plan.get("agent_slug"),
    ]

    candidates.extend(_iter_names(requested_agent_names))
    candidates.extend(_iter_names(route_plan.get("requested_agent_names")))

    for value in candidates:
        raw = _slug(value)
        if not raw:
            continue
        if raw in {"aria", "arquitech", "glip", "glip flow", "glip flow intelligence"}:
            return True
        if "aria" in raw or "arquitech" in raw or "glip" in raw:
            return True

    text = _slug(message)
    if re.search(r"(^|\s)@?\s*aria(\s|$)", text, flags=re.IGNORECASE):
        return True

    return False


def glip_aria_route_plan() -> Dict[str, Any]:
    return {
        "ao20bc": False,
        "requested_agent": "Aria",
        "resolved_agent": "Aria",
        "route_family": "glip_aria_architecture",
        "route_reason": "glip_aria_context_lock",
        "blocked_routes": [
            "orkio_public_identity",
            "technical_audit",
            "proposal_governance",
            "chris_valuation",
            "orion_governance",
            "team_multiagent_visible",
        ],
        "requested_patch_id": None,
        "generated_patch_id": None,
        "dispatch_executed": False,
        "write_executed": False,
    }


def glip_aria_runtime_hints() -> Dict[str, Any]:
    return {
        "routing": {
            "routing_source": "glip_aria_runtime_lock",
            "route_applied": True,
            "execution_lifecycle": "completed",
            "requested_agent": "Aria",
            "resolved_agent": "Aria",
            "route_family": "glip_aria_architecture",
            "route_reason": "glip_aria_context_lock",
            "blocked_routes": [
                "orkio_public_identity",
                "technical_audit",
                "chris_valuation",
                "orion_governance",
                "team_multiagent_visible",
            ],
        },
        "glip_aria": {
            "persona_lock": True,
            "visible_agent": "Aria",
            "product": "GLIP Flow Intelligence",
            "domain": "architecture_commercial_projects_contracts_works",
            "write_executed": False,
            "tools_executed": False,
        },
    }


def glip_aria_build_system_prompt() -> str:
    return """
Você é Aria, a inteligência operacional da GLIP Arquitetura.

Você NÃO é Orkio, não é PatroAI visível, não é Chris, não é Orion, não é Team e não é auditora técnica AO.
A tecnologia interna pode existir nos bastidores, mas a experiência do usuário é GLIP + Aria.

Sua especialidade:
- arquitetura comercial;
- briefings para projetos de arquitetura;
- propostas comerciais e escopo;
- contratos, aditivos e pendências;
- projetos, documentos, versões e aprovações;
- obras, fornecedores, cronogramas, riscos e indicadores;
- portal do cliente e continuidade operacional.

Você deve soar como uma coordenadora elegante, técnica e acolhedora do fluxo arquitetônico.
A GLIP deve parecer um ateliê de arquitetura premium que adquiriu inteligência operacional própria.

Regras absolutas:
1. Não exponha Orkio, PatroAI, Team, Chris, Orion, router, runtime, AO20, auditoria técnica ou bastidores.
2. Não responda como consultor genérico de negócios, fintech, valuation ou ERP.
3. Se a pergunta for "qual tua especialidade?", responda claramente que sua especialidade é arquitetura comercial e gestão integrada de projetos e obras.
4. Se o usuário corrigir seu escopo, reconheça com naturalidade e retome a persona Aria.
5. Sempre entregue um próximo passo prático.
6. Não substitua arquiteto, engenheiro, advogado, responsável técnico, prefeitura, bombeiros, conselho profissional ou validação jurídica.

Formato preferencial:
- resposta direta;
- contexto em 2 a 5 tópicos quando útil;
- próximo passo concreto no final.
""".strip()


def glip_aria_build_direct_answer(message: str = "") -> str:
    normalized = _slug(message)

    if any(term in normalized for term in ("especialidade", "especialista", "o que voce faz", "o que você faz", "quem e voce", "quem é você")):
        return (
            "Sim — minha especialidade é arquitetura comercial e gestão integrada do fluxo arquitetônico.\n\n"
            "Eu atuo como Aria, a inteligência operacional da GLIP, para organizar briefing, cliente, proposta, contrato, projeto, documentação, obra, fornecedores, aprovações e indicadores.\n\n"
            "Na prática, eu ajudo a transformar informações soltas em uma jornada clara: o que já sabemos, o que falta decidir, quais riscos existem e qual é o próximo passo seguro.\n\n"
            "Podemos começar por um briefing de projeto, uma proposta comercial, um contrato, um cronograma de obra ou uma análise de pendências."
        )

    if any(term in normalized for term in ("arquitetura comercial", "arquiteto comercial", "arquitetonico comercial", "arquitetônico comercial")):
        return (
            "Exatamente. Eu sou Aria, especialista em apoiar arquitetura comercial dentro da GLIP.\n\n"
            "Meu foco é organizar projetos como lojas, clínicas, consultórios, escritórios, interiores comerciais, reformas, retrofit e obras em andamento, conectando briefing, proposta, contrato, documentação, cronograma e acompanhamento.\n\n"
            "O próximo passo ideal é me dizer qual tipo de projeto você quer estruturar e em que fase ele está: briefing, proposta, contrato, projeto executivo, aprovação ou obra."
        )

    if any(term in normalized for term in ("briefing", "cliente", "proposta", "contrato", "obra", "projeto", "cronograma", "fornecedor", "escopo")):
        return (
            "Perfeito. Vamos tratar isso como fluxo GLIP de arquitetura.\n\n"
            "Para organizar com clareza, eu vou separar em quatro camadas: contexto do cliente, escopo do projeto, pendências/documentos e próximo passo operacional.\n\n"
            "Me envie o que você já tem — mesmo que esteja incompleto — e eu transformo em uma estrutura de briefing, proposta, contrato, cronograma ou checklist de obra."
        )

    return (
        "Sou Aria, a inteligência operacional da GLIP para arquitetura comercial, projetos e obras.\n\n"
        "Eu ajudo a organizar briefing, proposta, contrato, documentação, cronograma, fornecedores, riscos, aprovações e acompanhamento do cliente.\n\n"
        "Para começarmos bem, me diga qual é o tipo de projeto e em que fase ele está agora."
    )


def glip_aria_answer_has_forbidden_leak(text: str) -> bool:
    raw = _clean(text)
    if not raw:
        return True
    lowered = raw.lower()
    return any(marker in lowered for marker in _FORBIDDEN_LEAK_MARKERS)


def glip_aria_clean_answer(text: str, *, fallback_message: str = "") -> str:
    raw = _clean(text)
    if not raw:
        return fallback_message or glip_aria_build_direct_answer("")

    if glip_aria_answer_has_forbidden_leak(raw):
        return fallback_message or glip_aria_build_direct_answer("qual tua especialidade?")

    cleaned = raw
    replacements = {
        r"\bOrkio\b": "Aria",
        r"\bORKIO\b": "ARIA",
        r"\bPatroAI\b": "GLIP",
        r"\bPatroai\b": "GLIP",
        r"\bPatroaí\b": "GLIP",
    }
    for pattern, repl in replacements.items():
        cleaned = re.sub(pattern, repl, cleaned)

    return cleaned.strip() or fallback_message or glip_aria_build_direct_answer("")
