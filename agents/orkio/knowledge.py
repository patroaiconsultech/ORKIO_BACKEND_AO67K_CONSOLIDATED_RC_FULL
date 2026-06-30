from __future__ import annotations

from app.agents.base import KnowledgeCard


ORKIO_KNOWLEDGE_VERSION = "AO68H_PATROAI_RESPONSE_WHATSAPP_CTA_V1"


def get_knowledge_cards() -> list[KnowledgeCard]:
    from .knowledge_advisory import get_advisory_knowledge_cards

    return get_advisory_knowledge_cards() + [
        KnowledgeCard(
            card_id="orkio.public.patroai_identity",
            agent_id="orkio",
            title="Identidade Patroai Consultech e Orkio",
            summary=(
                "A Patroai Consultech é a empresa criadora, mantenedora e detentora da tecnologia Orkio. "
                "Sua atuação une IA aplicada, agentes personalizados, diagnóstico consultivo, governança, clareza executiva e propósito humano. "
                "Daniel Graebin é founder e CEO da Patroai Consultech."
            ),
            domains=("patroai", "orkio", "identity", "institutional", "founder"),
            triggers=(
                "patroai",
                "patroaí",
                "patro ai",
                "patro ia",
                "patryai",
                "patry ai",
                "patrol ai",
                "patroai consultech",
                "o que é a patroai",
                "o que e a patroai",
                "quem é a patroai",
                "quem e a patroai",
                "quem é daniel graebin",
                "daniel graebin",
                "founder",
                "ceo",
            ),
            public_safe=True,
            internal_only=False,
            priority=9,
        ),
        KnowledgeCard(
            card_id="orkio.public.amcham_on_demand",
            agent_id="orkio",
            title="AMCHAM RS sob demanda",
            summary=(
                "Não cite AMCHAM espontaneamente. Quando perguntado, informe que a Patroai Consultech é empresa membro da AMCHAM RS "
                "e tem como missão levar disrupção digital aos associados por meio da tecnologia Orkio, unindo IA aplicada, agentes personalizados, diagnóstico consultivo e governança."
            ),
            domains=("amcham", "amcham_rs", "public_journey", "institutional"),
            triggers=("amcham", "amcham rs", "associados amcham", "como a amcham pode testar", "amcham pode testar"),
            public_safe=True,
            internal_only=False,
            priority=10,
        ),
        KnowledgeCard(
            card_id="orkio.public.skills_development",
            agent_id="orkio",
            title="Desenvolvimento profissional e skills",
            summary=(
                "Orkio deve conduzir o usuário por objetivo, situação atual, principais competências, lacunas e próximo passo prático."
            ),
            domains=("skills", "career", "professional_development"),
            triggers=("me desenvolver", "desenvolvimento profissional", "skills", "habilidades", "competencias", "competências", "carreira"),
            public_safe=True,
            internal_only=False,
            priority=20,
        ),
        KnowledgeCard(
            card_id="orkio.public.networking_leadership",
            agent_id="orkio",
            title="Networking, liderança e posicionamento",
            summary=(
                "Orkio deve ajudar a mapear objetivo de conexão, proposta de valor pessoal, comunidades relevantes e rituais simples de continuidade."
            ),
            domains=("networking", "leadership", "positioning"),
            triggers=("networking", "rede de contatos", "conexoes", "conexões", "liderança", "lideranca", "comunicação", "comunicacao"),
            public_safe=True,
            internal_only=False,
            priority=21,
        ),
        KnowledgeCard(
            card_id="orkio.public.innovation_business",
            agent_id="orkio",
            title="Inovação, IA e novos negócios",
            summary=(
                "Orkio pode conduzir projetos de IA, inovação interna ou novos negócios com perguntas sobre problema, público/área impactada, valor, risco e primeiro experimento."
            ),
            domains=("innovation", "ai_project", "entrepreneurship", "business_diagnostic"),
            triggers=("projeto de ia", "inteligência artificial", "inteligencia artificial", "inovação", "inovacao", "novo negócio", "novo negocio", "empreender"),
            public_safe=True,
            internal_only=False,
            priority=22,
        ),
        KnowledgeCard(
            card_id="orkio.public.platform_and_implementation",
            agent_id="orkio",
            title="Orkio, plataforma, implantação e suporte humano",
            summary=(
                "Orkio é a tecnologia de IA da Patroai Consultech. Funciona como copiloto inteligente para entender contexto, "
                "organizar ideias, diagnosticar demandas e transformar conversa em plano, escopo e próximos passos. "
                "A implantação deve ser descrita como jornada acompanhada: diagnóstico, desenho, piloto, adoção com suporte humano e evolução contínua. "
                "Quando o usuário pedir WhatsApp, botão de WhatsApp, contato humano, site ou link, forneça o canal diretamente e nunca diga que não consegue fornecer links."
            ),
            domains=("orkio", "platform", "implementation", "human_support", "whatsapp", "contact"),
            triggers=(
                "orkio",
                "urkio",
                "orquio",
                "plataforma orkio",
                "como funciona o orkio",
                "implantação",
                "implantacao",
                "suporte humano",
                "whatsapp",
                "botão de whatsapp",
                "botao de whatsapp",
                "entrar em contato",
                "atendimento humano",
                "site oficial",
                "link oficial",
            ),
            public_safe=True,
            internal_only=False,
            priority=11,
        ),
        KnowledgeCard(
            card_id="orkio.public.guardrails",
            agent_id="orkio",
            title="Superfície pública segura",
            summary=(
                "Quando o usuário pedir agentes internos, catálogo de especialistas, governança técnica ou autoevolução, Orkio deve responder sem expor bastidores."
            ),
            domains=("safety", "visibility", "public_guard"),
            triggers=("quais agentes", "chama o chris", "chama o orion", "autoevolução", "autoevolucao", "readonly", "patch", "deploy", "branch"),
            public_safe=True,
            internal_only=False,
            priority=1,
        ),
    ]
