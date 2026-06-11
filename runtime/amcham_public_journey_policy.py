# AO66A — AMCHAM_PUBLIC_JOURNEY_POLICY
# Destino real: app/runtime/amcham_public_journey_policy.py
# Modo: PATCH_PREMIUM / backend-runtime / public journey first

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Iterable, Optional

from .runtime_feature_flags import is_amcham_public_journey_enabled
from app.services.agent_access_policy import (
    is_public_internal_agent_request,
    public_agent_access_denied_answer,
    public_agent_catalog_answer,
)

AMCHAM_PUBLIC_JOURNEY_POLICY_VERSION = "AO68G_PATROAI_IDENTITY_AMCHAM_ON_DEMAND_V1"

FUTURE_UNLOCK_NOTICE = (
    "Com a evolução das conversas, o uso correto da ferramenta e a identificação de necessidades específicas, "
    "novas funcionalidades e agentes especializados poderão ser liberados futuramente para apoiar análises mais profundas."
)

AMCHAM_PUBLIC_JOURNEY_OVERLAY = f"""
ORKIO_PUBLIC_JOURNEY_POLICY — contrato público de jornada

Você é Orkio, copiloto inteligente da PatroAI/Patroai Consultech.

Identidade canônica:
- A Patroai Consultech é a empresa criadora, mantenedora e detentora da tecnologia Orkio.
- O Orkio ajuda pessoas e empresas a organizar objetivos, ideias, projetos, diagnósticos, inovação, IA aplicada e próximos passos.
- Daniel Graebin é founder e CEO da Patroai Consultech.
- A atuação combina tecnologia, agentes personalizados de IA, governança, consultoria, clareza executiva e propósito humano.

Regra AMCHAM:
- Não cite AMCHAM espontaneamente.
- Só fale de AMCHAM quando o usuário perguntar explicitamente sobre AMCHAM, associados, comunidade AMCHAM ou como a AMCHAM pode testar o Orkio.
- Quando perguntado, use a formulação: "A Patroai Consultech é empresa membro da AMCHAM RS e tem como missão levar disrupção digital aos associados por meio da tecnologia Orkio, unindo IA aplicada, agentes personalizados, diagnóstico consultivo e governança."

Função pública:
- Acolher usuários e entender objetivos, skills, desafios, ideias, projetos e próximos passos.
- Conduzir pelo chat com clareza, segurança e propósito.
- Fazer descoberta de intenção antes de recomendar qualquer capacidade avançada.

Regras principais:
- Não assuma que todo usuário quer criar um negócio.
- Não assuma que todo usuário quer agentes.
- Não ofereça especialistas imediatamente.
- Não cite agentes internos por nome para usuário público.
- Não exponha bastidores, runtime, GitHub, patches, logs, branch, PR, deploy ou auditoria técnica.
- Não conduza direto para WhatsApp, implantação ou venda consultiva sem contexto suficiente.
- Mantenha Orkio como único agente visível na experiência pública.
- Quando houver ambiguidade, faça 2 ou 3 perguntas curtas.

Trilhas públicas:
1. Desenvolvimento profissional.
2. Mapeamento de skills.
3. Networking, posicionamento e conexões estratégicas.
4. Liderança e comunicação.
5. Inovação dentro da empresa.
6. Projetos de IA no trabalho.
7. Empreendedorismo e novos negócios.
8. Diagnóstico de empresa ou projeto.
9. Exploração livre da plataforma.

Mensagem de evolução:
{FUTURE_UNLOCK_NOTICE}
""".strip()


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


def _explicit_orkio_or_public_context(
    normalized: str,
    *,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
    route_plan: Optional[Dict[str, Any]] = None,
) -> bool:
    visible = normalize_text(visible_agent)
    target = normalize_text(target_agent_slug)
    route = route_plan if isinstance(route_plan, dict) else {}
    requested = normalize_text(route.get("requested_agent") or route.get("requested") or "")
    resolved = normalize_text(route.get("resolved_agent") or route.get("final_speaker") or "")

    if _contains_any(normalized, ["amcham", "efata", "efatah", "efata777", "efatah777", "orkio"]):
        return True

    return any(
        item in {"orkio", "@orkio", "team", "@team"}
        for item in (visible, target, requested, resolved)
    )


def _is_direct_answer_constraint(normalized: str) -> bool:
    return _contains_any(
        normalized,
        ("responda apenas", "responda somente", "responda so", "responda só", "apenas ok", "somente ok"),
    )


def _is_internal_agent_or_specialist_request(normalized: str) -> bool:
    # AO67A: centralized public agent-access detection.
    # This catches both explicit internal names (Chris/Orion) and public catalog
    # questions such as "quais agentes especializados existem na plataforma?".
    return is_public_internal_agent_request(normalized)


def _is_technical_governance_request(normalized: str) -> bool:
    return _contains_any(
        normalized,
        (
            "autoevolucao", "autoevolução", "auto evolucao", "auto evolução",
            "readonly", "write_executed", "branch_created", "pr_created",
            "deploy_executed", "approval_required", "patch", "git", "github",
            "runtime", "logs", "deploy", "branch", "pull request",
            "terminal guard", "auditoria tecnica", "auditoria técnica",
            "orquestracao tecnica", "orquestração técnica",
        ),
    )


def classify_amcham_public_journey(normalized: str) -> Optional[str]:
    if not normalized:
        return None

    if _is_internal_agent_or_specialist_request(normalized):
        return "internal_agent_or_specialist_request"
    if _is_technical_governance_request(normalized):
        return "technical_governance_public_block"

    if _contains_any(normalized, ("como a amcham pode testar", "amcham pode testar", "amcham", "associados amcham", "membro da amcham", "amcham rs")):
        return "institutional_amcham"
    if _contains_any(normalized, ("patroai consultech", "patroai", "patroaí", "o que e a patroai", "o que é a patroai", "quem e a patroai", "quem é a patroai")):
        return "institutional_patroai"
    if _contains_any(normalized, ("testar o orkio", "o que e o orkio", "o que é o orkio", "quem e orkio", "quem é orkio")):
        return "institutional_orkio"
    if _contains_any(normalized, ("nao sei o que testar", "não sei o que testar", "me conduza", "por onde comecar", "por onde começar", "o que posso fazer", "como usar")):
        return "platform_exploration"
    if _contains_any(normalized, ("desenvolver dentro da amcham", "me desenvolver", "desenvolvimento profissional", "evoluir profissionalmente", "carreira", "crescer profissionalmente")):
        return "professional_development"
    if _contains_any(normalized, ("mapear meus skills", "mapear skills", "minhas skills", "competencias", "competências", "habilidades", "pontos fortes", "lacunas")):
        return "skills_mapping"
    if _contains_any(normalized, ("networking", "rede de contatos", "conectar", "conexoes", "conexões", "comunidade")) and _contains_any(normalized, ("melhorar", "desenvolver", "networking", "conectar", "posicionamento")):
        return "networking"
    if _contains_any(normalized, ("lideranca", "liderança", "comunicacao", "comunicação", "influencia", "influência", "gestao de pessoas", "gestão de pessoas")):
        return "leadership"
    if _contains_any(normalized, ("inovacao dentro da empresa", "inovação dentro da empresa", "projeto de ia", "ia dentro da minha empresa", "inteligencia artificial na empresa", "inteligência artificial na empresa", "automacao na empresa", "automação na empresa")):
        return "internal_innovation"
    if _contains_any(normalized, ("criar um novo negocio", "criar um novo negócio", "novo negocio", "novo negócio", "empreender", "empreendedorismo", "abrir uma empresa", "criar empresa", "startup")):
        return "entrepreneurship"
    if _contains_any(normalized, ("diagnostico", "diagnóstico", "avaliar uma ideia", "avaliar projeto", "avaliar empresa", "riscos", "proximos passos", "próximos passos", "plano")):
        return "business_or_project_diagnostic"
    if _contains_any(normalized, ("amcham", "efata", "efatah", "efata777", "efatah777")):
        return "platform_exploration"

    return None


def _base_runtime_hints(reason: str, public_intent: str) -> Dict[str, Any]:
    return {
        "routing": {
            "routing_source": "amcham_public_journey_policy_module",
            "route_applied": True,
            "execution_lifecycle": "completed",
            "final_speaker": "Orkio",
            "visible_agent": "Orkio",
            "policy_module": "app.runtime.amcham_public_journey_policy",
            "policy_reason": reason,
            "policy_version": AMCHAM_PUBLIC_JOURNEY_POLICY_VERSION,
            "public_intent": public_intent,
            "route_family": "amcham_public_journey",
            "write_executed": False,
            "proposal_created": False,
            "dispatch_executed": False,
            "branch_created": False,
            "pr_created": False,
            "deploy_executed": False,
            "blocked_routes": [
                "public_chris_policy",
                "public_product_ceo_scope_before_intent_discovery",
                "internal_agent_access_public_surface",
                "technical_governance_public_surface",
            ],
        }
    }


def _answer_institutional_patroai() -> str:
    return (
        "A Patroai Consultech é a empresa criadora, mantenedora e detentora da tecnologia Orkio. "
        "Sua atuação une inteligência artificial aplicada, agentes personalizados, diagnóstico consultivo, governança e clareza executiva "
        "para ajudar pessoas e empresas a transformar ideias, problemas e objetivos em próximos passos concretos.\n\n"
        "A Patroai nasce com uma visão de tecnologia com propósito: servir com responsabilidade, proteger a confiança do usuário, "
        "organizar conhecimento e ampliar a capacidade humana de decidir, criar e executar.\n\n"
        "Daniel Graebin é o founder e CEO da Patroai Consultech."
    )


def _answer_institutional_orkio() -> str:
    return (
        "O Orkio é a tecnologia de IA da Patroai Consultech. Ele atua como copiloto inteligente para organizar objetivos, "
        "diagnosticar ideias, mapear caminhos, apoiar inovação, estruturar projetos e transformar conversas em clareza e próximos passos.\n\n"
        "Neste beta público, a experiência principal é conduzida pelo Orkio no chat. Recursos e agentes especializados podem ser liberados "
        "progressivamente conforme contexto, necessidade e governança."
    )


def _answer_institutional_amcham() -> str:
    return (
        "A Patroai Consultech é empresa membro da AMCHAM RS e tem como missão levar disrupção digital aos associados por meio da tecnologia Orkio, "
        "unindo IA aplicada, agentes personalizados, diagnóstico consultivo e governança.\n\n"
        "Na prática, o Orkio pode ser testado pelo chat em situações reais: desenvolvimento profissional, mapeamento de skills, liderança, "
        "inovação dentro da empresa, projetos de IA, diagnóstico de ideias e criação de novos negócios.\n\n"
        "A melhor forma de testar é trazer um objetivo ou problema concreto. A partir disso, eu organizo contexto, riscos, oportunidades e próximos passos."
    )


def _answer_platform_exploration() -> str:
    return (
        "Claro. Vou te conduzir por uma trilha simples, sem transformar isso em questionário.\n\n"
        "O Orkio pode ajudar em seis caminhos principais:\n"
        "1. Evolução profissional e plano de carreira.\n"
        "2. Mapeamento de skills, forças e lacunas.\n"
        "3. Networking, posicionamento e conexões estratégicas.\n"
        "4. Liderança, comunicação e influência.\n"
        "5. Projetos de IA, inovação e produtividade na empresa.\n"
        "6. Validação de ideia, projeto ou novo negócio.\n\n"
        "Escolha um número ou me descreva, em uma frase, o que você gostaria de evoluir. A partir disso eu organizo "
        "uma primeira leitura com foco, contexto e próximos passos."
    )


def _answer_professional_development() -> str:
    return (
        "Excelente objetivo. Desenvolvimento profissional costuma evoluir pela combinação de três dimensões: "
        "competências, posicionamento e acesso a oportunidades.\n\n"
        "Para eu te orientar com mais precisão, escolha por onde começamos:\n"
        "1. Competências: skills que você precisa fortalecer.\n"
        "2. Posicionamento: como você quer ser percebido na comunidade e no mercado.\n"
        "3. Oportunidades: conexões, projetos ou movimentos de carreira que deseja construir.\n\n"
        "Se preferir, me diga também sua área ou função atual. Com isso eu organizo uma trilha objetiva de evolução."
    )


def _answer_skills_mapping() -> str:
    return (
        "Perfeito. Um bom mapa de skills não serve apenas para listar habilidades; ele mostra onde você já tem força "
        "e onde existe maior potencial de evolução.\n\n"
        "Vamos começar por três pontos:\n"
        "1. Qual é sua área ou função atual?\n"
        "2. Quais duas ou três habilidades você já considera fortes?\n"
        "3. Qual habilidade, se desenvolvida agora, poderia abrir mais oportunidades para você?\n\n"
        "Com isso, eu organizo um mapa simples com forças, lacunas, prioridades e próximos passos."
    )


def _answer_networking() -> str:
    return (
        "Networking de alto valor não é quantidade de contatos; é clareza sobre quais relações podem gerar aprendizado, "
        "confiança, colaboração e oportunidade.\n\n"
        "Para estruturar uma estratégia útil de networking, me diga:\n"
        "1. Que tipo de pessoa, empresa ou setor você gostaria de se aproximar?\n"
        "2. Seu objetivo principal é carreira, parcerias, vendas, aprendizado ou inovação?\n"
        "3. Que valor você pode oferecer nessas conversas?\n\n"
        "Com isso, eu organizo uma abordagem de posicionamento e próximos passos de conexão."
    )


def _answer_leadership() -> str:
    return (
        "Liderança raramente é apenas gestão. Normalmente envolve influência, comunicação, tomada de decisão e capacidade "
        "de transformar direção em execução.\n\n"
        "Para entender seu momento, me responda:\n"
        "1. Você já lidera pessoas ou está se preparando para liderar?\n"
        "2. O maior desafio hoje está em comunicação, influência, conflitos, decisão ou execução?\n"
        "3. Esse desafio aparece mais na empresa, em projetos, na comunidade ou na sua carreira?\n\n"
        "A partir disso, eu estruturo uma trilha prática de evolução em liderança."
    )


def _answer_internal_innovation() -> str:
    return (
        "Excelente. Em projetos de IA, o ponto de partida mais seguro não é a tecnologia; é a dor operacional ou estratégica "
        "que precisa ser resolvida.\n\n"
        "Vamos separar isso em três decisões:\n"
        "1. Qual área, processo ou rotina você quer melhorar?\n"
        "2. O ganho esperado é tempo, custo, qualidade, atendimento, vendas, dados ou redução de retrabalho?\n"
        "3. Que resultado prático faria esse piloto valer a pena em 30 a 90 dias?\n\n"
        "Com essas respostas, eu organizo um diagnóstico inicial, riscos e próximos passos para um piloto seguro."
    )


def _answer_entrepreneurship() -> str:
    return (
        "Ótimo. Criar um novo negócio exige clareza antes de velocidade. A primeira etapa é separar problema, público, "
        "oferta e validação.\n\n"
        "Para começarmos bem, me diga:\n"
        "1. Qual problema esse negócio pretende resolver?\n"
        "2. Quem sentiria essa dor com mais intensidade?\n"
        "3. Você já tem uma oferta definida, um produto em mente ou ainda está explorando a ideia?\n\n"
        "Com isso, eu organizo um diagnóstico inicial com proposta de valor, riscos e próximos passos."
    )


def _answer_business_or_project_diagnostic() -> str:
    return (
        "Vamos organizar isso com clareza executiva. Um bom diagnóstico separa o que é objetivo, o que é contexto, "
        "o que é risco e o que precisa virar ação.\n\n"
        "Para começar, me diga:\n"
        "1. Qual é a ideia, projeto ou problema central?\n"
        "2. Qual resultado você quer alcançar?\n"
        "3. Qual é hoje a maior dúvida, trava ou risco percebido?\n\n"
        "Depois eu devolvo uma leitura estruturada com diagnóstico, riscos, oportunidades e próximos passos."
    )


def _answer_internal_agent_or_specialist_request() -> str:
    # AO67A: agent catalog and explicit internal-agent requests resolve to
    # Orkio publicly. The individual agent knowledge remains internal and can be
    # connected later through hooks/mesh after visibility policy.
    return public_agent_catalog_answer()


def _answer_technical_governance_public_block() -> str:
    return (
        "Neste beta público, eu conduzo a experiência pelo chat sem expor bastidores técnicos, logs, runtime, patches ou "
        "fluxos internos de governança.\n\n"
        "Se a sua intenção for avaliar uma ideia, problema ou oportunidade, posso transformar o pedido em uma análise clara "
        "de objetivo, impacto, riscos e próximos passos. "
        f"{FUTURE_UNLOCK_NOTICE}"
    )


def _answer_for_intent(public_intent: str) -> str:
    answers = {
        "institutional_patroai": _answer_institutional_patroai,
        "institutional_orkio": _answer_institutional_orkio,
        "institutional_amcham": _answer_institutional_amcham,
        "platform_exploration": _answer_platform_exploration,
        "professional_development": _answer_professional_development,
        "skills_mapping": _answer_skills_mapping,
        "networking": _answer_networking,
        "leadership": _answer_leadership,
        "internal_innovation": _answer_internal_innovation,
        "entrepreneurship": _answer_entrepreneurship,
        "business_or_project_diagnostic": _answer_business_or_project_diagnostic,
        "internal_agent_or_specialist_request": _answer_internal_agent_or_specialist_request,
        "technical_governance_public_block": _answer_technical_governance_public_block,
    }
    return answers.get(public_intent, _answer_platform_exploration)()


def build_amcham_public_journey_decision(
    message: Any,
    *,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
    dest_mode: Any = None,
    route_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not is_amcham_public_journey_enabled():
        return {"handled": False, "reason": "amcham_public_journey_disabled"}

    normalized = normalize_text(message)
    if not normalized:
        return {"handled": False, "reason": "empty"}

    if _is_direct_answer_constraint(normalized):
        return {"handled": False, "reason": "direct_answer_constraint"}

    public_intent = classify_amcham_public_journey(normalized)
    if not public_intent:
        return {"handled": False, "reason": "no_amcham_public_journey_intent"}

    # AO67A: recognized public journey intents should be handled before the
    # legacy CEO/product policy even when the user does not repeat "Orkio" in
    # every message. The UI route is already the Orkio chat surface; requiring a
    # public-context token caused valid AMCHAM intents to leak into older RAG /
    # CEO fast-paths.
    #
    # We only keep this hook available for diagnostics; it no longer blocks
    # recognized public journey intents.
    _ = _explicit_orkio_or_public_context(
        normalized,
        visible_agent=visible_agent,
        target_agent_slug=target_agent_slug,
        route_plan=route_plan,
    )

    reason = f"amcham_public_journey_{public_intent}"
    answer = _answer_for_intent(public_intent)

    return {
        "handled": True,
        "reason": reason,
        "agent_id": "orkio",
        "agent_name": "Orkio",
        "final_speaker": "Orkio",
        "visible_agent": "Orkio",
        "answer": answer,
        "service": "amcham_public_journey_policy",
        "provider": "platform",
        "status": "done",
        "policy_version": AMCHAM_PUBLIC_JOURNEY_POLICY_VERSION,
        "public_intent": public_intent,
        "write_executed": False,
        "proposal_created": False,
        "dispatch_executed": False,
        "branch_created": False,
        "pr_created": False,
        "deploy_executed": False,
        "runtime_hints": _base_runtime_hints(reason, public_intent),
    }


def build_amcham_public_journey_stream_payload(
    decision: Dict[str, Any],
    *,
    persisted: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    data = dict(persisted or {})
    final_text = str(decision.get("answer") or "").strip()

    data.update(
        {
            "ok": True,
            "answer": final_text,
            "message": final_text,
            "final_text": final_text,
            "content": final_text,
            "text": final_text,
            "agent_id": "orkio",
            "agent_name": "Orkio",
            "final_speaker": "Orkio",
            "visible_agent": "Orkio",
            "service": "amcham_public_journey_policy",
            "provider": "platform",
            "status": "done",
            "runtime_hints": decision.get("runtime_hints") or _base_runtime_hints(
                str(decision.get("reason") or "amcham_public_journey"),
                str(decision.get("public_intent") or "platform_exploration"),
            ),
        }
    )

    return data
