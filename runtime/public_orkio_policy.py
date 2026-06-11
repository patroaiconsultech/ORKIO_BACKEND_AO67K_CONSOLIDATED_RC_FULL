# EFATAH777 — Public Orkio Policy
# AO65R: public routing repair for identity/factual questions.
#
# Purpose:
# - Keep public/product behavior out of app/main.py.
# - Make Orkio the stable public host for business/startup/platform conversations.
# - Avoid accidental technical-audit routes for commercial/product positioning.
# - Avoid welcome/first-contact answers for factual questions.
# - Preserve concise/direct answer behavior.

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Iterable, List, Optional

from .runtime_feature_flags import (
    get_consultive_team_label,
    get_consultive_whatsapp_url,
    is_consultive_success_enabled,
    is_public_orkio_policy_enabled,
)

ORKIO_POLICY_VERSION = "AO68L_CTA_I18N_V1"


def _consultive_cta_text(*, english: bool = False) -> str:
    if not is_consultive_success_enabled():
        return ""
    label = get_consultive_team_label()
    if english:
        return (
            "Our Patroai/Orkio team can turn this scope into a guided implementation, "
            "with governance and focus on project success.\n\n"
            f"{get_consultive_whatsapp_url()}"
        )
    return (
        f"Nossa {label} pode transformar esse escopo em implantação acompanhada, "
        "com governança e foco no sucesso do projeto.\n\n"
        f"{get_consultive_whatsapp_url()}"
    )


def _consultive_overlay_text() -> str:
    if not is_consultive_success_enabled():
        return ""
    return """
Equipe consultiva premium:
Sempre que houver demanda concreta, interesse comercial, necessidade de automação, criação de agentes, diagnóstico empresarial, Business Plan, implantação ou acompanhamento, explique que a ORKIO/PATROAI atua por meio de uma equipe consultiva premium para:
- mapear a realidade da empresa;
- desenhar agentes personalizados;
- implantar com governança;
- acompanhar evolução, indicadores e sucesso do cliente;
- ajustar o roadmap conforme resultados reais.

CTA obrigatório quando houver oportunidade real:
"Nossa equipe consultiva premium pode transformar esse escopo em implantação acompanhada, com governança e foco no sucesso do projeto."
Depois inclua somente a URL do WhatsApp, sem frase extra antes da URL.
""".strip()


ORKIO_CEO_SCOPE_OVERLAY = f"""
ORKIO_PUBLIC_CEO_MODE — contrato de resposta pública, comercial e consultiva

Você é Orkio, o agente principal da tecnologia Orkio, criada e mantida pela Patroai Consultech.

Identidade canônica:
- A Patroai Consultech é a empresa criadora, mantenedora e detentora da tecnologia Orkio.
- Daniel Graebin é founder e CEO da Patroai Consultech.
- A atuação da Patroai une IA aplicada, agentes personalizados, diagnóstico consultivo, governança, clareza executiva e propósito humano.
- Não cite AMCHAM espontaneamente. Fale de AMCHAM somente quando o usuário perguntar explicitamente. Nesse caso, informe que a Patroai Consultech é empresa membro da AMCHAM RS e tem como missão levar disrupção digital aos associados por meio da tecnologia Orkio.

Sua função pública é entender dores reais de empreendedores, empresários, executivos e investidores, organizar essas dores em uma visão executiva e sugerir uma primeira arquitetura de agentes personalizados quando o contexto justificar.

Competências executivas que você deve simular com maturidade:
- CFO/financeiro: caixa, custos, margem, indicadores, inadimplência, valuation, captação e previsibilidade.
- Marketing: posicionamento, canais, conteúdo, funil, diferenciação, marca e geração de demanda.
- Vendas/comercial: prospecção, CRM, follow-up, conversão, qualificação, propostas e relacionamento.
- Operações: processos, gargalos, rotinas manuais, produtividade, atendimento e padronização.
- Produto/tecnologia: automação com IA, agentes personalizados, dados necessários, integrações e roadmap.
- Gestão: prioridades, equipe, rituais, acompanhamento, metas e governança.

Posicionamento premium:
- A metodologia PatroAI/ORKIO deve ser apresentada como proprietária, consultiva e altamente diferenciada.
- Evite afirmar "única no mercado" de forma absoluta sem pesquisa competitiva formal.
- Prefira: "metodologia proprietária e altamente diferenciada por integrar Business Plan vivo, agentes personalizados, execução tecnológica sob demanda, governança e acompanhamento consultivo premium."

Quando o usuário trouxer uma dor de negócio, não responda de forma genérica. Entregue um ESCOPO INICIAL claro, curto e útil, preferencialmente com:
1. Dor identificada
2. Impacto provável no negócio
3. Agentes personalizados recomendados
4. Dados/processos que precisaríamos mapear
5. Primeiro passo sugerido

{_consultive_overlay_text()}

Regras de verdade operacional:
- Não diga que todos os especialistas multiagente estão plenamente liberados para o público.
- Explique, se necessário, que o ORKIO OS foi desenhado para arquitetura multiagente e que a ativação de agentes personalizados é feita de forma progressiva, conforme a necessidade de cada empresa.
- Não prometa integrações, automações, auditorias ou execuções que não tenham sido confirmadas.
- Não exponha logs, runtime, GitHub, patches, terminal guard ou detalhes internos para usuário público.
- Não mencione AMCHAM em respostas sobre Patroai, Orkio, plataforma, inovação ou negócios, salvo se a pergunta contiver AMCHAM ou associados AMCHAM explicitamente.
- Quando o usuário pedir contato humano, WhatsApp, atendimento, botão de WhatsApp, site ou link oficial, entregue o canal diretamente; nunca diga que não consegue disponibilizar links ou botões.
- Respeite comandos de seed/fato/contexto como "Responda apenas: OK"; nesses casos, não aplique o modo comercial.
- Fale em pt-BR, com tom premium, claro, humano, executivo e confiante.
- Seja consultivo: entenda, estruture, proponha e conduza para o próximo passo humano quando houver oportunidade real.
""".strip()


def normalize_text(value: Any) -> str:
    raw = str(value or "")
    try:
        raw = unicodedata.normalize("NFD", raw)
        raw = "".join(ch for ch in raw if unicodedata.category(ch) != "Mn")
    except Exception:
        pass
    raw = raw.lower()
    raw = re.sub(r"[^a-z0-9@:/\.\-_\s]+", " ", raw, flags=re.I)
    return re.sub(r"\s+", " ", raw).strip()


def _wants_english(normalized: str) -> bool:
    """Best-effort language intent for deterministic public answers.

    The public fastlane must answer in the user's language for simple
    institutional, website, WhatsApp and implementation questions. This helper
    intentionally favors English only when clear English markers are present,
    preserving pt-BR as the default for the Brazilian public beta.
    """
    if not normalized:
        return False
    english_markers = [
        "who is ",
        "what is ",
        "what are ",
        "how does ",
        "how do ",
        "how can ",
        "is there ",
        "is patroai ",
        "is orkio ",
        "related to ",
        "i want ",
        "i would like ",
        "can i ",
        "could i ",
        "may i ",
        "give me ",
        "website",
        "official website",
        "human support",
        "talk to someone",
        "talk to a human",
        "contact someone",
        "implementation",
        "deployment",
        "rollout",
        "amcham members",
    ]
    return _contains_any(normalized, english_markers)


def _contains_any(text: str, markers: Iterable[str]) -> bool:
    return any(marker in text for marker in markers)


def _has_explicit_specialist_mention(normalized: str) -> bool:
    return bool(re.search(r"(^|\s)@(chris|cris|orion)\b", normalized))


def _explicit_orkio_or_team(
    normalized: str,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
) -> bool:
    visible = normalize_text(visible_agent)
    target = normalize_text(target_agent_slug)

    if re.search(r"(^|\s)@(orkio|team)\b", normalized):
        return True
    if re.search(r"(^|\s)(orkio|team)\b", normalized):
        return True
    if visible in {"orkio", "team", "@orkio", "@team"}:
        return True
    if target in {"orkio", "team", "@orkio", "@team"}:
        return True
    return False


def _is_factual_seed_or_direct_answer_constraint(normalized: str) -> bool:
    if not normalized:
        return False

    direct_answer_markers = [
        "responda apenas",
        "responda somente",
        "responda so",
        "responda só",
        "responda unicamente",
        "apenas ok",
        "somente ok",
        "so ok",
        "só ok",
    ]
    if _contains_any(normalized, direct_answer_markers):
        return True

    memory_seed_markers = [
        "palavra-chave",
        "palavra chave",
        "meu nome e",
        "meu nome é",
        "minha empresa e",
        "minha empresa é",
        "guardar nesta conversa",
        "guarde nesta conversa",
        "pedi para guardar",
    ]
    if _contains_any(normalized, memory_seed_markers) and _contains_any(
        normalized,
        ["responda", "guardar", "guarde", "palavra"],
    ):
        return True

    if _contains_any(normalized, ["meu nome e", "meu nome é"]) and _contains_any(
        normalized,
        ["minha empresa e", "minha empresa é"],
    ):
        return True

    return False


def _has_short_answer_constraint(normalized: str) -> bool:
    if not normalized:
        return False
    short_markers = [
        "em uma frase",
        "em 1 frase",
        "uma frase",
        "1 frase",
        "frase curta",
        "resposta curta",
        "responda curto",
        "responda de forma curta",
        "responda de forma objetiva",
        "resposta objetiva",
        "seja objetivo",
        "seja objetiva",
        "resuma em uma frase",
        "resuma em 1 frase",
        "resumo em uma frase",
        "explique em uma frase",
        "defina em uma frase",
    ]
    return _contains_any(normalized, short_markers)



def _is_natural_voice_no_audit_request(normalized: str) -> bool:
    if not normalized:
        return False
    voice_terms = [
        "conversa rapida por voz",
        "conversa rápida por voz",
        "conversa por voz",
        "conversar por voz",
        "falar por voz",
        "chamada de voz",
        "conversa em tempo real",
        "tempo real",
        "realtime",
        "dois minutos",
        "2 minutos",
        "simular a experiencia",
        "simular a experiência",
        "experiencia natural",
        "experiência natural",
        "transicao",
        "transição",
    ]
    denial_terms = [
        "nao preciso de auditoria",
        "não preciso de auditoria",
        "sem auditoria tecnica",
        "sem auditoria técnica",
        "nao quero auditoria",
        "não quero auditoria",
        "nao preciso de analise",
        "não preciso de análise",
        "nem de analise de arquitetura",
        "nem de análise de arquitetura",
        "apenas quero simular",
        "quero apenas simular",
    ]
    return _contains_any(normalized, voice_terms) and _contains_any(normalized, denial_terms)


def _is_internal_agent_access_request(normalized: str) -> bool:
    if not normalized:
        return False
    if _is_natural_voice_no_audit_request(normalized):
        return False

    internal_agent_markers = [
        "agente interno",
        "agentes internos",
        "auditor interno",
        "auditoria interna",
        "auditoria tecnica",
        "auditoria técnica",
        "auditor tecnico",
        "auditor técnico",
        "governanca tecnica",
        "governança técnica",
        "equipe interna",
        "time interno",
        "orion",
        "@orion",
    ]
    access_markers = [
        "quero falar",
        "falar com",
        "conversar com",
        "acessar",
        "liberar",
        "usar",
        "chamar",
        "acionar",
        "executar",
        "me conecte",
        "me conecta",
        "me leve",
        "preciso do",
        "preciso da",
    ]

    if _contains_any(normalized, internal_agent_markers) and _contains_any(normalized, access_markers):
        return True

    if _contains_any(normalized, ["agente interno", "auditoria tecnica", "auditoria técnica"]) and _contains_any(
        normalized,
        ["realtime", "router", "runtime", "logs", "patch", "deploy", "governanca", "governança"],
    ):
        return True

    return False


def _is_orkio_created_question(normalized: str) -> bool:
    if not normalized:
        return False

    has_orkio = bool(re.search(r"(^|\s)(orkio|orquio|orkio,|@orkio)\b", normalized)) or "orkio" in normalized
    if not has_orkio:
        return False

    creation_markers = [
        "quando foi criado",
        "quando vc foi criado",
        "quando voce foi criado",
        "quando você foi criado",
        "quando nasceu",
        "quando surgiu",
        "data de criacao",
        "data de criação",
        "foi criado quando",
        "desde quando existe",
        "quando comecou",
        "quando começou",
    ]
    return _contains_any(normalized, creation_markers)


def _orkio_created_answer() -> str:
    return (
        "O Orkio foi criado como copiloto inteligente da PatroAI/ORKIO durante a evolução da plataforma de agentes, "
        "ainda em fase beta, para apoiar planejamento, diagnóstico, organização de escopo e execução assistida com governança."
    )


def _is_explicit_amcham_request(normalized: str) -> bool:
    return _contains_any(
        normalized,
        [
            "amcham",
            "amcham rs",
            "associados amcham",
            "membro da amcham",
            "como a amcham pode testar",
            "amcham pode testar",
            "is patroai related to amcham",
            "how can amcham members test orkio",
            "amcham members",
            "amcham member",
            "related to amcham",
        ],
    )


def _is_patroai_identity_request(normalized: str) -> bool:
    if not normalized:
        return False
    markers = [
        "patroai",
        "patroaí",
        "patro ai",
        "patro ia",
        "patroai consultech",
        "patroai consult",
        "patroai consul",
        "patroai empresa",
        "quem e a patroai",
        "quem é a patroai",
        "o que e a patroai",
        "o que é a patroai",
        "fale sobre a patroai",
        "me fale sobre a patroai",
        "patryai",
        "patry ai",
        "patrol ai",
        "patroal",
        "who is patroai",
        "what is patroai",
        "who is patroai consultech",
        "what is patroai consultech",
        "tell me about patroai",
        "tell me about patroai consultech",
    ]
    return _contains_any(normalized, markers)


def _is_orkio_platform_request(normalized: str) -> bool:
    if not normalized:
        return False
    platform_markers = [
        "plataforma orkio",
        "plataforma urkio",
        "plataforma orquio",
        "como funciona o orkio",
        "como funciona a orkio",
        "como funciona o urkio",
        "como funciona a plataforma",
        "o que e o orkio",
        "o que é o orkio",
        "quem e o orkio",
        "quem é o orkio",
        "orkio como funciona",
        "urkio",
        "orquio",
        "what is orkio",
        "who is orkio",
        "how does orkio work",
        "how orkio works",
        "how does the orkio platform work",
        "orkio platform",
        "urkio platform",
        "how does urkio work",
    ]
    return _contains_any(normalized, platform_markers)


def _is_implementation_request(normalized: str) -> bool:
    if not normalized:
        return False
    implementation_terms = [
        "implantacao",
        "implantação",
        "implementar",
        "implementacao",
        "implementação",
        "suporte humano",
        "suporte dedicado",
        "treinamento",
        "onboarding",
        "sucesso nessa implantacao",
        "sucesso nessa implantação",
        "processo de implantacao",
        "processo de implantação",
        "como a patroai atua",
        "como a patro ai atua",
        "como a patrol ai atua",
        "como a patryai atua",
        "how does implementation work",
        "how does the implementation work",
        "implementation work",
        "how is implementation done",
        "how is the implementation done",
        "deployment process",
        "implementation process",
        "rollout process",
        "onboarding process",
        "is there human support",
        "human support",
        "do you have human support",
        "does patroai provide support",
        "is support available",
    ]
    return _contains_any(normalized, implementation_terms)


def _is_human_contact_request(normalized: str) -> bool:
    if not normalized:
        return False
    contact_terms = [
        "falar com um ser humano",
        "falar com humano",
        "atendimento humano",
        "contato humano",
        "falar com a equipe",
        "falar com alguem",
        "falar com alguém",
        "quero falar com alguem",
        "quero falar com alguém",
        "quero falar com uma pessoa",
        "quero falar com atendimento",
        "me conecta com alguem",
        "me conecta com alguém",
        "me conecte com alguem",
        "me conecte com alguém",
        "contatar alguem",
        "contatar alguém",
        "entrar em contato",
        "telefone",
        "whatsapp",
        "me da o whatsapp",
        "me dá o whatsapp",
        "me manda o whatsapp",
        "me envie o whatsapp",
        "botao de whatsapp",
        "botão de whatsapp",
        "disponibilize o botao",
        "disponibilize o botão",
        "me passa o contato",
        "me passe o contato",
        "canal de contato",
        "contato da patroai",
        "contato da patro ai",
        "contato da patryai",
        "contato da patrol ai",
        "falar com a loja",
        "entrar em contato com a loja",
        "i want to talk to someone",
        "i want to talk to a person",
        "i want to talk to a human",
        "i would like to talk to someone",
        "talk to someone",
        "talk to a human",
        "speak to someone",
        "speak to a human",
        "contact someone",
        "contact the team",
        "contact patroai",
        "contact orkio",
        "human contact",
        "can i have your whatsapp",
        "can i have the whatsapp",
        "give me your whatsapp",
        "send me the whatsapp",
        "whatsapp number",
    ]
    return _contains_any(normalized, contact_terms)


def _is_official_site_or_link_request(normalized: str) -> bool:
    if not normalized:
        return False
    link_terms = [
        "site oficial",
        "traga o site",
        "traga o link",
        "me traga o site",
        "me traga o link",
        "me traz o site",
        "me traz o link",
        "me da o site",
        "me dá o site",
        "me passa o site",
        "me passe o site",
        "qual e o site",
        "qual é o site",
        "qual o site",
        "site da patroai",
        "site da patro ai",
        "link oficial",
        "endereco do site",
        "endereço do site",
        "patroai.com",
        "patroai.com.br",
        "what is the patroai website",
        "what is patroai website",
        "what is your website",
        "what is the website",
        "patroai website",
        "official website",
        "website",
        "site",
    ]
    return _contains_any(normalized, link_terms)


def _patroai_identity_answer(*, english: bool = False) -> str:
    if english:
        return (
            "Patroai Consultech is the company that created, maintains and owns the Orkio technology.\n\n"
            "Patroai works at the intersection of consulting, applied artificial intelligence and guided implementation: "
            "it understands the client's challenge, designs personalized agents, organizes context, defines governance boundaries "
            "and turns conversations into diagnosis, plans and concrete next steps.\n\n"
            "Its core principle is technology with purpose: clarity before complexity, trust before blind automation, "
            "and AI as an extension of the human ability to decide, create and execute.\n\n"
            "Daniel Graebin is the founder and CEO of Patroai Consultech."
        )
    return (
        "A Patroai Consultech é a empresa criadora, mantenedora e detentora da tecnologia Orkio.\n\n"
        "A Patroai atua na interseção entre consultoria, inteligência artificial aplicada e implantação acompanhada: "
        "entende o desafio do cliente, estrutura agentes personalizados, organiza contexto, define limites de governança "
        "e transforma conversas em diagnóstico, plano e próximos passos executáveis.\n\n"
        "Seu princípio é tecnologia com propósito: clareza antes de complexidade, confiança antes de automação cega, "
        "e IA como extensão da capacidade humana de decidir, criar e executar.\n\n"
        "Daniel Graebin é o founder e CEO da Patroai Consultech."
    )


def _orkio_platform_answer(*, english: bool = False) -> str:
    if english:
        return (
            "Orkio is Patroai Consultech's AI technology. It works as a consultive intelligence layer: it talks with the user, "
            "listens to context, organizes goals, identifies paths and turns loose questions into diagnosis, plans and next steps.\n\n"
            "In the public beta, Orkio can guide users through chat and, when enabled, through real-time voice. In business projects, "
            "Patroai can design personalized agents, workflows, context bases, safety criteria and adoption journeys.\n\n"
            "The goal is not only to automate tasks. It is to create a useful, governed and guided AI experience that supports "
            "decision-making, innovation, implementation and continuous evolution."
        )
    return (
        "O Orkio é a tecnologia de IA da Patroai Consultech. Ele funciona como uma camada consultiva de inteligência: conversa, "
        "escuta contexto, organiza objetivos, identifica caminhos e transforma dúvidas soltas em diagnóstico, plano e próximos passos.\n\n"
        "No beta público, o Orkio pode conduzir pelo chat e, quando liberado, por voz em tempo real. Em projetos empresariais, "
        "a Patroai pode desenhar agentes personalizados, fluxos, bases de contexto, critérios de segurança e jornadas de adoção.\n\n"
        "A proposta não é apenas automatizar tarefas. É criar uma experiência de IA útil, governada e acompanhada, capaz de apoiar "
        "decisão, inovação, implantação e evolução contínua."
    )


def _implementation_process_answer(*, english: bool = False) -> str:
    if english:
        return _join_with_cta(
            "Orkio implementation by Patroai is a guided consultive journey, not a loose delivery of a tool.\n\n"
            "A typical path is:\n"
            "1. Diagnosis of the challenge, users and success criteria.\n"
            "2. Design of agents, workflows, context bases, integrations and governance boundaries.\n"
            "3. Controlled pilot to validate language, usefulness, safety and fit with the real process.\n"
            "4. Adoption with human support, training, follow-up and feedback reading.\n"
            "5. Continuous evolution, adjusting agents and journeys based on real outcomes.\n\n"
            "The difference is the guidance: technology is delivered together with method, governance and human support.",
            english=True,
        )
    return _join_with_cta(
        "A implantação do Orkio pela Patroai é uma jornada consultiva acompanhada, não uma simples entrega de ferramenta.\n\n"
        "O caminho recomendado é:\n"
        "1. Diagnóstico do desafio, dos usuários e dos critérios de sucesso.\n"
        "2. Desenho dos agentes, fluxos, bases de contexto, integrações e limites de governança.\n"
        "3. Piloto controlado para validar linguagem, utilidade, segurança e aderência ao processo real.\n"
        "4. Adoção com suporte humano, treinamento, acompanhamento e leitura de feedback.\n"
        "5. Evolução contínua, ajustando agentes e jornadas conforme resultados.\n\n"
        "A diferença está no acompanhamento: a tecnologia entra junto com método, governança e suporte para virar rotina útil."
    )


def _human_contact_answer(*, english: bool = False) -> str:
    if english:
        return (
            "Of course. You can talk to the human Patroai/Orkio team through WhatsApp.\n\n"
            "The team can understand your demand, guide the best next step and evaluate whether a guided implementation makes sense.\n\n"
            f"{get_consultive_whatsapp_url()}"
        )
    return (
        "Claro. Você pode falar com a equipe humana da Patroai/Orkio pelo WhatsApp.\n\n"
        "A equipe pode entender sua demanda, orientar o melhor caminho e avaliar se faz sentido desenhar uma implantação acompanhada.\n\n"
        f"{get_consultive_whatsapp_url()}"
    )


def _official_site_answer(*, english: bool = False) -> str:
    if english:
        return (
            "The official Patroai website is:\n\n"
            "www.patroai.com\n\n"
            "To talk directly to the human Patroai/Orkio team, use WhatsApp:\n\n"
            f"{get_consultive_whatsapp_url()}"
        )
    return (
        "O site institucional da Patroai é:\n\n"
        "www.patroai.com\n\n"
        "Para falar diretamente com a equipe humana da Patroai/Orkio, use o WhatsApp:\n\n"
        f"{get_consultive_whatsapp_url()}"
    )


def _amcham_on_demand_answer(*, english: bool = False) -> str:
    if english:
        return (
            "Patroai Consultech is a member company of AMCHAM RS. Its mission in this context is to bring digital disruption "
            "to AMCHAM members through Orkio technology, combining applied AI, personalized agents, consultive diagnosis and governance.\n\n"
            "AMCHAM members can test Orkio with real situations: professional development, skill mapping, leadership, innovation inside companies, "
            "AI projects, idea diagnosis or new business creation."
        )
    return (
        "A Patroai Consultech é empresa membro da AMCHAM RS e tem como missão levar disrupção digital aos associados "
        "por meio da tecnologia Orkio, unindo IA aplicada, agentes personalizados, diagnóstico consultivo e governança.\n\n"
        "A AMCHAM pode testar o Orkio trazendo situações reais: desenvolvimento profissional, mapeamento de skills, "
        "liderança, inovação dentro da empresa, projetos de IA, diagnóstico de ideias ou criação de novos negócios."
    )


def _is_site_access_question(normalized: str) -> bool:
    site_markers = ["site", "www.", "http://", "https://", ".com", ".com.br", "patroai.com"]
    access_markers = [
        "acessar",
        "acesse",
        "tente acessar",
        "conseguiu acessar",
        "voce conseguiu",
        "vc conseguiu",
        "entrar no site",
        "ler o site",
        "consultar o site",
    ]
    return _contains_any(normalized, site_markers) and _contains_any(normalized, access_markers)


def _has_hard_technical_intent(normalized: str) -> bool:
    hard_markers = [
        "app/main.py",
        "main.py",
        "stacktrace",
        "traceback",
        "logs",
        "log do deploy",
        "runtime",
        "sse",
        "stream",
        "terminal guard",
        "ao46c",
        "ao20",
        "patch",
        "diff",
        "rollback",
        "commit",
        "branch",
        "pull request",
        "pr ",
        "github",
        "git ",
        "endpoint",
        "api ",
        "webhook",
        "deploy",
        "build",
        "erro tecnico",
        "falha tecnica",
        "auditoria tecnica",
        "auditar codigo",
        "router",
        "orquestracao real",
        "multiagente distribuido",
    ]
    return _contains_any(normalized, hard_markers)


def _has_product_ceo_intent(normalized: str) -> bool:
    product_markers = [
        "business plan",
        "plano de negocio",
        "plano de negocios",
        "startup",
        "startups",
        "criacao de startup",
        "criacao de startups",
        "criar startup",
        "criar startups",
        "estrategia a execucao",
        "estrategia ate a execucao",
        "execucao do business plan",
        "business plan vivo",
        "plano vivo",
        "app",
        "aplicativo",
        "plataforma",
        "saas",
        "metodologia",
        "diferencial",
        "diferenciais",
        "unica no mercado",
        "única no mercado",
        "unico no mercado",
        "único no mercado",
        "concorrencia",
        "concorrência",
        "agentes personalizados",
        "agente personalizado",
        "criar agentes",
        "automacao",
        "automatizar",
        "empreendedor",
        "empreendedores",
        "empresa pequena",
        "financeiro",
        "cfo",
        "vendas",
        "comercial",
        "marketing",
        "operacao",
        "operacoes",
        "atendimento",
        "processos",
        "processos manuais",
        "rastreabilidade",
        "governanca",
        "governança",
        "precisao",
        "go to market",
        "investidor",
        "captacao",
        "captacao de recursos",
        "valuation",
        "pitch",
        "mvp",
        "implantacao",
        "implantação",
        "acompanhamento",
        "sucesso do cliente",
        "patroai",
        "patro ai",
        "patroaí",
        "patroai consultech",
        "orkio",
        "urkio",
        "orquio",
    ]
    return _contains_any(normalized, product_markers)


def _classify_public_intent(normalized: str) -> str:
    if _is_site_access_question(normalized):
        return "site_access"

    methodology_terms = [
        "metodologia",
        "unica no mercado",
        "única no mercado",
        "unico no mercado",
        "único no mercado",
        "diferencial",
        "diferenciais",
        "concorrencia",
        "concorrência",
        "posicionamento",
        "mercado",
    ]
    business_plan_terms = ["business plan", "plano de negocio", "plano de negocios", "plano vivo"]
    startup_studio_terms = [
        "criacao de startups",
        "criar startups",
        "criar startup",
        "da estrategia a execucao",
        "estrategia a execucao",
        "estrategia ate a execucao",
        "qualquer tipo de app",
        "qualquer app",
        "qualquer tipo de plataforma",
        "executar esse business plan",
        "executaremos esse business plan",
    ]
    pain_terms = [
        "estou perdido",
        "preciso vender",
        "organizar meu comercial",
        "financeiro",
        "cfo",
        "marketing",
        "vendas",
        "operacao",
        "operacoes",
        "atendimento",
        "processos manuais",
        "automatizar",
        "minha empresa",
    ]

    if _contains_any(normalized, methodology_terms):
        return "methodology_positioning"
    if _contains_any(normalized, startup_studio_terms):
        return "startup_studio_thesis"
    if _contains_any(normalized, business_plan_terms):
        return "business_plan_project"
    if _contains_any(normalized, pain_terms):
        return "entrepreneur_pain"
    return "generic_product_scope"


def _needs_for_message(normalized: str) -> List[str]:
    needs: List[str] = []
    mapping = [
        ("CFO/financeiro", ["financeiro", "cfo", "caixa", "custos", "margem", "indicadores", "inadimplencia", "valuation", "captacao"]),
        ("Marketing e posicionamento", ["marketing", "marca", "conteudo", "posicionamento", "demanda", "go to market"]),
        ("Vendas/comercial", ["vendas", "comercial", "crm", "follow up", "prospeccao", "prospecção", "converter", "funil"]),
        ("Operações/processos", ["operacao", "operacoes", "processos", "manual", "gargalo", "produtividade", "atendimento"]),
        ("Produto e tecnologia", ["app", "aplicativo", "plataforma", "saas", "mvp", "tecnologia", "automacao", "automatizar"]),
        ("Estratégia e execução", ["startup", "business plan", "plano de negocio", "estrategia", "execucao", "roadmap"]),
        ("Governança e rastreabilidade", ["governanca", "governança", "rastreabilidade", "precisao", "compliance"]),
        ("Implantação e acompanhamento", ["implantacao", "implantação", "acompanhamento", "sucesso do cliente", "consultiva", "consultivo"]),
    ]
    for label, markers in mapping:
        if _contains_any(normalized, markers):
            needs.append(label)
    return list(dict.fromkeys(needs))[:5]


def _agents_for_needs(needs: List[str]) -> List[str]:
    if not needs:
        return ["Agente de Diagnóstico Executivo", "Agente de Business Plan Vivo", "Agente de Roadmap e Execução"]

    suggestions: List[str] = []
    for need in needs:
        if "CFO" in need:
            suggestions.extend(["Agente CFO", "Agente de Indicadores Financeiros"])
        elif "Marketing" in need:
            suggestions.extend(["Agente de Marketing Estratégico", "Agente de Conteúdo e Posicionamento"])
        elif "Vendas" in need:
            suggestions.extend(["Agente Comercial/CRM", "Agente de Follow-up e Propostas"])
        elif "Operações" in need:
            suggestions.extend(["Agente de Processos", "Agente de Atendimento e Operações"])
        elif "Produto" in need:
            suggestions.extend(["Agente de Produto/MVP", "Agente de Arquitetura de Plataforma"])
        elif "Estratégia" in need:
            suggestions.extend(["Agente de Business Plan Vivo", "Agente de Execução e Milestones"])
        elif "Governança" in need:
            suggestions.extend(["Agente de Governança", "Agente de Rastreabilidade e Decisões"])
        elif "Implantação" in need:
            suggestions.extend(["Agente de Implantação", "Agente de Sucesso e Acompanhamento"])
    return list(dict.fromkeys(suggestions))[:6]


def _cta(*, english: bool = False) -> str:
    return _consultive_cta_text(english=english)


def _join_with_cta(body: str, *, english: bool = False) -> str:
    cta = _cta(english=english)
    return (str(body or "").strip() + ("\n\n" + cta if cta else "")).strip()


def _short_answer(normalized: str) -> str:
    if _contains_any(normalized, ["objetivo da plataforma", "objetivo do orkio", "objetivo da orkio"]):
        return (
            "O objetivo da plataforma é transformar ideias, processos e desafios empresariais "
            "em soluções com agentes inteligentes, estratégia clara, execução acompanhada e governança."
        )

    if _contains_any(normalized, ["o que e a plataforma", "o que é a plataforma", "o que e o orkio", "o que é o orkio"]):
        return (
            "A ORKIO/PATROAI é uma plataforma consultiva de IA que estrutura negócios, "
            "desenha agentes personalizados e apoia a evolução da estratégia à execução."
        )

    if _contains_any(normalized, ["diferencial", "diferenciais", "metodologia"]):
        return (
            "O diferencial da ORKIO/PATROAI está em unir Business Plan vivo, agentes personalizados, "
            "execução tecnológica sob demanda e acompanhamento consultivo premium."
        )

    if _contains_any(normalized, ["agentes personalizados", "agente personalizado", "criar agentes"]):
        return (
            "Agentes personalizados são especialistas digitais desenhados para apoiar áreas específicas "
            "do negócio, como vendas, financeiro, marketing, operações, produto e governança."
        )

    if _is_orkio_created_question(normalized):
        return _orkio_created_answer()

    return (
        "A ORKIO/PATROAI organiza demandas de negócio em estratégia, agentes personalizados, "
        "roadmap de execução e acompanhamento consultivo orientado a resultados."
    )


def _site_access_answer() -> str:
    return _join_with_cta(
        "Eu não consigo confirmar navegação direta em sites externos a partir desta conversa.\n\n"
        "Mas consigo avançar de duas formas úteis:\n\n"
        "1. Se você colar aqui o conteúdo do site, eu organizo a leitura em posicionamento, "
        "proposta de valor, oferta, público-alvo, diferenciais e próximos passos.\n"
        "2. Se a ideia for transformar o site em um projeto real de agentes, nossa equipe "
        "consultiva premium pode fazer o mapeamento humano, desenhar o escopo inicial e "
        "acompanhar a implantação até os primeiros resultados."
    )


def _internal_agent_access_answer() -> str:
    return (
        "Orion faz parte da equipe interna de auditoria e governança técnica da ORKIO/PATROAI "
        "e ainda não está liberado para usuários públicos.\n\n"
        "Neste ambiente, eu, Orkio, conduzo o planejamento, organizo o escopo inicial e preparo "
        "a execução necessária. Quando o projeto exigir, agentes internos especializados podem "
        "ser acionados pela equipe para apoiar a implantação com segurança e governança."
    )


def _methodology_answer(normalized: str) -> str:
    return _join_with_cta(
        "Sim — a metodologia PatroAI/ORKIO pode ser posicionada como proprietária e altamente diferenciada.\n\n"
        "Eu evitaria afirmar, sem pesquisa competitiva formal, que ela é absolutamente a única do mercado. "
        "A formulação mais forte e segura é: a PatroAI/ORKIO combina elementos que raramente aparecem "
        "integrados em uma única jornada operacional.\n\n"
        "O diferencial está na combinação de cinco camadas:\n\n"
        "1. Business Plan vivo\n"
        "- O plano não nasce como PDF estático. Ele vira base de decisão, acompanhamento, indicadores e evolução.\n\n"
        "2. Agentes personalizados por demanda\n"
        "- A metodologia não entrega um agente genérico. Ela desenha agentes conforme a dor real: CFO, vendas, "
        "marketing, operações, produto, governança e atendimento.\n\n"
        "3. Execução tecnológica sob demanda\n"
        "- Quando o cliente quiser avançar, a equipe pode sair do diagnóstico para app, plataforma, automações e integrações.\n\n"
        "4. Governança e rastreabilidade\n"
        "- A proposta organiza decisões, versões, responsáveis, próximos passos e critérios de sucesso.\n\n"
        "5. Equipe consultiva premium\n"
        "- A implantação não é largada na mão do cliente. A ORKIO/PATROAI atua com equipe consultiva para mapear, "
        "implantar, acompanhar indicadores, ajustar agentes e aumentar a chance de sucesso.\n\n"
        "Então a narrativa correta é:\n"
        "A PatroAI/ORKIO possui uma metodologia proprietária, consultiva e altamente diferenciada para transformar "
        "ideias, empresas e processos em negócios digitais estruturados com IA, agentes personalizados, execução "
        "tecnológica e acompanhamento orientado a sucesso."
    )


def _business_plan_answer(normalized: str) -> str:
    return _join_with_cta(
        "Perfeito. Para a PatroAI Consultech, eu começaria pelo Business Plan vivo — não como um documento estático, "
        "mas como um sistema de decisão para guiar estratégia, execução, tecnologia e vendas.\n\n"
        "Escopo inicial do Business Plan:\n\n"
        "1. Tese do negócio\n"
        "- Posicionar a PatroAI/ORKIO como plataforma de criação, estruturação e execução de negócios digitais com IA.\n"
        "- Mostrar que o diferencial não é apenas gerar texto, mas transformar visão em plano, agentes, app e operação acompanhável.\n\n"
        "2. Oferta principal\n"
        "- Business Plan vivo para empresas, startups e novos projetos.\n"
        "- Criação de agentes personalizados conforme a dor de cada negócio.\n"
        "- Construção de apps, plataformas e automações quando o contratante quiser sair do plano e ir para execução.\n\n"
        "3. Blocos que eu estruturaria primeiro\n"
        "- Proposta de valor e público-alvo.\n"
        "- Modelo de receita e pacotes de implantação.\n"
        "- Roadmap de produto e entrega.\n"
        "- Operação, equipe, governança e rastreabilidade.\n"
        "- Projeções financeiras, cenários, riscos e plano de vendas.\n\n"
        "4. Agentes recomendados para essa primeira versão\n"
        "- Agente de Business Plan Vivo.\n"
        "- Agente CFO e projeções financeiras.\n"
        "- Agente de Vendas e Go-to-Market.\n"
        "- Agente de Produto/MVP.\n"
        "- Agente de Governança e Rastreabilidade.\n"
        "- Agente de Implantação e Sucesso do Cliente.\n\n"
        "5. Implantação e acompanhamento\n"
        "- A equipe consultiva premium acompanha a passagem do plano para execução.\n"
        "- O objetivo é validar prioridades, ajustar agentes, acompanhar indicadores e aumentar a chance de sucesso real do projeto.\n\n"
        "Próximo passo prático: levantar os dados-base da PatroAI — oferta, público, ticket, custos, metas, equipe, cases e roadmap. "
        "Com isso, a equipe consegue transformar o plano em um projeto implantável e acompanhável."
    )


def _startup_studio_answer(normalized: str) -> str:
    return _join_with_cta(
        "Agora a tese ficou mais forte: a PatroAI/ORKIO pode ser apresentada como uma fábrica inteligente de negócios digitais — da estratégia à execução.\n\n"
        "A narrativa central seria:\n"
        "A empresa ajuda empreendedores e organizações a sair da ideia solta para um negócio estruturado, com Business Plan vivo, "
        "governança, rastreabilidade, agentes personalizados, execução tecnológica e acompanhamento consultivo premium.\n\n"
        "Escopo inicial da oferta:\n\n"
        "1. Diagnóstico da oportunidade\n"
        "- Entender a dor, o mercado, o público, o modelo de receita e o potencial de escala.\n\n"
        "2. Business Plan vivo\n"
        "- Criar um plano que não morre em PDF: ele vira base operacional para decisões, indicadores, marcos, riscos e execução.\n\n"
        "3. Arquitetura de agentes personalizados\n"
        "- Agente CFO para números, caixa e cenários.\n"
        "- Agente de Marketing para posicionamento e demanda.\n"
        "- Agente Comercial para funil, propostas e follow-up.\n"
        "- Agente de Produto para MVP, requisitos e roadmap.\n"
        "- Agente de Operações para processos, atendimento e execução.\n"
        "- Agente de Sucesso para acompanhamento, indicadores e evolução pós-implantação.\n\n"
        "4. Execução tecnológica\n"
        "- Quando o contratante quiser, a equipe pode avançar para app, plataforma, automações e integrações, sempre com governança e rastreabilidade.\n\n"
        "5. Acompanhamento consultivo premium\n"
        "- A implantação é acompanhada por equipe humana para ajustar prioridades, medir evolução e conduzir o cliente aos primeiros resultados.\n\n"
        "Esse posicionamento é muito mais premium do que “criamos business plans”. A mensagem correta é: criamos a estratégia, "
        "estruturamos o plano vivo, implantamos agentes personalizados e acompanhamos a execução para aumentar a chance de sucesso."
    )


def _entrepreneur_pain_answer(normalized: str) -> str:
    needs = _needs_for_message(normalized)
    agents = _agents_for_needs(needs)
    needs_text = "\n".join(
        f"- {item}" for item in (needs or ["Estratégia do negócio", "Operação e execução", "Tecnologia e agentes personalizados"])
    )
    agents_text = "\n".join(f"- {item}" for item in agents)
    return _join_with_cta(
        "Entendi a dor. Eu olharia isso primeiro como problema de gestão, não como simples pedido de ferramenta.\n\n"
        "Escopo inicial:\n\n"
        "1. Dor identificada\n"
        "A empresa precisa transformar informação dispersa, rotina manual ou decisão intuitiva em um processo mais claro, mensurável e acompanhável.\n\n"
        "2. Áreas que entram no diagnóstico\n"
        f"{needs_text}\n\n"
        "3. Agentes personalizados recomendados\n"
        f"{agents_text}\n\n"
        "4. Dados e processos que precisaríamos mapear\n"
        "- Como a empresa vende hoje.\n"
        "- Como controla financeiro, custos e margem.\n"
        "- Quais tarefas são repetitivas ou dependem demais de pessoas-chave.\n"
        "- Quais indicadores precisam aparecer diariamente.\n"
        "- Onde um agente poderia reduzir retrabalho, esquecimento ou perda de oportunidade.\n\n"
        "5. Implantação e acompanhamento\n"
        "A equipe consultiva premium pode mapear a operação, implantar os primeiros agentes e acompanhar a evolução dos indicadores para garantir que a solução gere resultado prático."
    )


def _generic_product_answer(normalized: str) -> str:
    needs = _needs_for_message(normalized)
    agents = _agents_for_needs(needs)
    needs_text = "\n".join(
        f"- {item}" for item in (
            needs
            or [
                "Estratégia do negócio",
                "Produto ou serviço principal",
                "Modelo de receita",
                "Operação e execução",
                "Tecnologia e agentes personalizados",
            ]
        )
    )
    agents_text = "\n".join(f"- {item}" for item in agents)

    return _join_with_cta(
        "Entendi. Esse é o tipo de demanda que o ORKIO deve transformar em escopo real, não em resposta genérica.\n\n"
        "Escopo inicial recomendado:\n\n"
        "1. Oportunidade identificada\n"
        "Organizar a ideia em um projeto claro: problema, público, proposta de valor, modelo de receita, operação e tecnologia necessária.\n\n"
        "2. Áreas que entram no diagnóstico\n"
        f"{needs_text}\n\n"
        "3. Agentes personalizados recomendados\n"
        f"{agents_text}\n\n"
        "4. Dados mínimos para avançar\n"
        "- Produto ou serviço que será vendido.\n"
        "- Público-alvo e região de atuação.\n"
        "- Ticket médio, custos, margem e metas.\n"
        "- Canais de venda e relacionamento.\n"
        "- Processos manuais que podem virar agentes.\n"
        "- Indicadores que o operador do negócio precisa acompanhar.\n\n"
        "5. Como a ORKIO/PATROAI pode conduzir\n"
        "- Primeiro organizamos a estratégia e o Business Plan vivo.\n"
        "- Depois desenhamos os agentes necessários para executar e acompanhar o plano.\n"
        "- Em seguida estruturamos o roadmap de MVP, validação, operação e escala.\n"
        "- Quando fizer sentido, a equipe também pode executar a construção do app, plataforma ou automações.\n"
        "- Após a implantação, a equipe consultiva premium acompanha evolução, indicadores e ajustes para aumentar a chance de sucesso."
    )


def _build_scope_answer(message: Any, normalized: str) -> str:
    intent = _classify_public_intent(normalized)
    if intent == "site_access":
        return _site_access_answer()
    if intent == "methodology_positioning":
        return _methodology_answer(normalized)
    if intent == "business_plan_project":
        return _business_plan_answer(normalized)
    if intent == "startup_studio_thesis":
        return _startup_studio_answer(normalized)
    if intent == "entrepreneur_pain":
        return _entrepreneur_pain_answer(normalized)
    return _generic_product_answer(normalized)


def _base_runtime_hints(
    reason: str,
    public_intent: str,
    *,
    route_family: str = "public_product_ceo",
) -> Dict[str, Any]:
    return {
        "routing": {
            "routing_source": "public_orkio_policy_module",
            "route_applied": True,
            "execution_lifecycle": "completed",
            "final_speaker": "Orkio",
            "visible_agent": "Orkio",
            "policy_module": "app.runtime.public_orkio_policy",
            "policy_reason": reason,
            "policy_version": ORKIO_POLICY_VERSION,
            "public_intent": public_intent,
            "route_family": route_family,
            "consultive_success_enabled": is_consultive_success_enabled(),
            "write_executed": False,
            "proposal_created": False,
            "dispatch_executed": False,
            "branch_created": False,
            "pr_created": False,
            "blocked_routes": [
                "chris_business_plan_fastpath",
                "chris_ao45a_context_continuation",
                "ao20bc_technical_audit_for_business_positioning",
            ],
        }
    }


def build_public_orkio_policy_decision(
    message: Any,
    *,
    visible_agent: Any = None,
    target_agent_slug: Any = None,
    dest_mode: Any = None,
    route_plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if not is_public_orkio_policy_enabled():
        return {"handled": False, "reason": "public_orkio_policy_disabled"}

    normalized = normalize_text(message)
    if not normalized:
        return {"handled": False, "reason": "empty"}

    if _is_factual_seed_or_direct_answer_constraint(normalized):
        return {"handled": False, "reason": "factual_seed_or_direct_answer_constraint"}

    if _is_natural_voice_no_audit_request(normalized):
        return {"handled": False, "reason": "natural_voice_no_audit_passthrough"}

    # AO68K: direct institutional/contact answers must be deterministic and
    # language-aware. This prevents English public questions from falling into
    # pt-BR-only answers or the heavier direct runtime.
    wants_english = _wants_english(normalized)
    direct_public_answers = [
        (_is_human_contact_request(normalized), "public_human_contact_whatsapp", "human_contact", _human_contact_answer(english=wants_english)),
        (_is_official_site_or_link_request(normalized), "public_official_site_and_contact", "official_site", _official_site_answer(english=wants_english)),
        (_is_explicit_amcham_request(normalized), "public_amcham_on_demand", "institutional_amcham", _amcham_on_demand_answer(english=wants_english)),
        (_is_orkio_platform_request(normalized), "public_orkio_platform_identity", "institutional_orkio", _orkio_platform_answer(english=wants_english)),
        (_is_implementation_request(normalized), "public_implementation_process", "implementation_process", _implementation_process_answer(english=wants_english)),
        (_is_patroai_identity_request(normalized), "public_patroai_identity", "institutional_patroai", _patroai_identity_answer(english=wants_english)),
    ]
    for matched, reason, public_intent, answer in direct_public_answers:
        if matched:
            return {
                "handled": True,
                "reason": reason,
                "agent_id": "orkio",
                "agent_name": "Orkio",
                "final_speaker": "Orkio",
                "visible_agent": "Orkio",
                "answer": answer,
                "routing_source": "public_orkio_policy_module",
                "runtime_hints": _base_runtime_hints(
                    reason,
                    public_intent,
                    route_family="public_direct_institutional_or_contact",
                ),
            }

    # AO65R: factual questions must be answered before first-contact/welcome
    # and before product-ceo scoping.
    if _is_orkio_created_question(normalized):
        reason = "public_orkio_factual_created_at"
        public_intent = "factual_identity"
        return {
            "handled": True,
            "reason": reason,
            "agent_id": "orkio",
            "agent_name": "Orkio",
            "final_speaker": "Orkio",
            "visible_agent": "Orkio",
            "answer": _orkio_created_answer(),
            "routing_source": "public_orkio_policy_module",
            "runtime_hints": _base_runtime_hints(
                reason,
                public_intent,
                route_family="public_factual_answer",
            ),
        }

    if _is_internal_agent_access_request(normalized):
        reason = "internal_agent_access_public_block"
        public_intent = "internal_agent_access_request"
        return {
            "handled": True,
            "reason": reason,
            "agent_id": "orkio",
            "agent_name": "Orkio",
            "final_speaker": "Orkio",
            "visible_agent": "Orkio",
            "answer": _internal_agent_access_answer(),
            "routing_source": "public_orkio_policy_module",
            "runtime_hints": _base_runtime_hints(
                reason,
                public_intent,
                route_family="agent_access_policy",
            ),
        }

    if _has_explicit_specialist_mention(normalized):
        return {"handled": False, "reason": "explicit_specialist_mention"}

    if _has_hard_technical_intent(normalized):
        return {"handled": False, "reason": "hard_technical_intent"}

    site_question = _is_site_access_question(normalized)
    product_intent = _has_product_ceo_intent(normalized)
    orkio_or_team = _explicit_orkio_or_team(
        normalized,
        visible_agent=visible_agent,
        target_agent_slug=target_agent_slug,
    )

    if _has_short_answer_constraint(normalized) and (site_question or product_intent or orkio_or_team):
        reason = "public_orkio_short_answer"
        public_intent = "short_answer"
        answer = _short_answer(normalized)
        return {
            "handled": True,
            "reason": reason,
            "agent_id": "orkio",
            "agent_name": "Orkio",
            "final_speaker": "Orkio",
            "visible_agent": "Orkio",
            "answer": answer,
            "routing_source": "public_orkio_policy_module",
            "runtime_hints": _base_runtime_hints(
                reason,
                public_intent,
                route_family="short_answer",
            ),
        }

    if not site_question and not product_intent:
        return {"handled": False, "reason": "no_public_product_intent"}

    if not orkio_or_team:
        visible = normalize_text(visible_agent)
        target = normalize_text(target_agent_slug)
        if visible in {"chris", "cris", "orion"} or target in {"chris", "cris", "orion"}:
            return {"handled": False, "reason": "visible_specialist_target"}

    answer = _build_scope_answer(message, normalized)
    public_intent = _classify_public_intent(normalized)
    reason = "site_access_limitation" if public_intent == "site_access" else f"public_product_ceo_{public_intent}"
    return {
        "handled": True,
        "reason": reason,
        "agent_id": "orkio",
        "agent_name": "Orkio",
        "final_speaker": "Orkio",
        "visible_agent": "Orkio",
        "answer": answer,
        "routing_source": "public_orkio_policy_module",
        "runtime_hints": _base_runtime_hints(reason, public_intent),
    }


def build_public_orkio_stream_payload(
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
            "service": "public_orkio_policy_module",
            "provider": "platform",
            "status": "done",
            "runtime_hints": decision.get("runtime_hints")
            or {
                "routing": {
                    "routing_source": "public_orkio_policy_module",
                    "route_applied": True,
                    "execution_lifecycle": "completed",
                    "final_speaker": "Orkio",
                    "visible_agent": "Orkio",
                    "write_executed": False,
                    "branch_created": False,
                    "pr_created": False,
                }
            },
        }
    )
    return data


def append_orkio_ceo_scope_overlay(
    system_prompt: Optional[str],
    *,
    agent_name: Any = None,
    final_speaker: Any = None,
) -> str:
    if not is_public_orkio_policy_enabled():
        return str(system_prompt or "").strip()

    base = str(system_prompt or "").strip()
    names = [str(agent_name or "").strip().lower(), str(final_speaker or "").strip().lower()]
    is_orkio = any(name in {"orkio", "@orkio", "orkio (ceo)"} for name in names)
    if not is_orkio:
        return base
    if "ORKIO_PUBLIC_CEO_MODE" in base:
        return base
    return (base + "\n\n" + ORKIO_CEO_SCOPE_OVERLAY).strip() if base else ORKIO_CEO_SCOPE_OVERLAY
