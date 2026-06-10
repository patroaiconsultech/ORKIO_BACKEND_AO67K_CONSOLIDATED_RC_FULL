from __future__ import annotations

from app.agents.base import KnowledgeCard


ORKIO_KNOWLEDGE_VERSION = "AO67C_ORKIO_KNOWLEDGE_V1"


def get_knowledge_cards() -> list[KnowledgeCard]:
    return [
        KnowledgeCard(
            card_id="orkio.public.amcham_institutional",
            agent_id="orkio",
            title="Jornada pública AMCHAM/Efatà 777",
            summary=(
                "A experiência pública deve apresentar a PATROAI e o Orkio de forma simples, "
                "explicando como testar por chat em trilhas de carreira, skills, networking, liderança, inovação e negócios."
            ),
            domains=("amcham", "public_journey", "institutional"),
            triggers=("amcham", "patroai", "patroaí", "efata", "efatà", "testar o orkio", "como testar"),
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
