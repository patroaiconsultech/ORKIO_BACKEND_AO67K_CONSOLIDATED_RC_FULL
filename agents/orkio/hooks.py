from __future__ import annotations

from typing import Any, Dict, Optional

from app.agents.base import AgentHook, build_internal_advice
from .knowledge import get_knowledge_cards
from .profile import get_profile


ORKIO_HOOKS_VERSION = "AO83_ORKIO_WORLD_CLASS_ADVISOR_V1"


def get_hooks() -> list[AgentHook]:
    return [
        AgentHook(
            hook_id="orkio.advisory.executive_diagnosis",
            agent_id="orkio",
            family="advisory",
            label="diagnostico executivo",
            description="Converte ambiguidade em diagnostico, decisao, prioridade e proxima acao mensuravel.",
            triggers=("diagnostico", "decisao", "estrategia", "prioridade", "objetivo", "problema", "recomende", "primeiro passo"),
            priority=2,
            public_safe=True,
            internal_only=False,
            synthesis_role="executive_advisory",
        ),
        AgentHook(
            hook_id="orkio.advisory.roadmap",
            agent_id="orkio",
            family="planning",
            label="roadmap executivo",
            description="Estrutura roadmaps com fases, owners, entregaveis, dependencias, KPIs, riscos e gates.",
            triggers=("roadmap", "plano de acao", "cronograma", "30 60 90", "implementar", "etapas", "execucao"),
            priority=3,
            public_safe=True,
            internal_only=False,
            synthesis_role="roadmap_architect",
        ),
        AgentHook(
            hook_id="orkio.advisory.multidisciplinary_synthesis",
            agent_id="orkio",
            family="synthesis",
            label="sintese multidisciplinar",
            description="Integra estrategia, cliente, financas, operacoes, pessoas, tecnologia, governanca e risco conforme relevancia.",
            triggers=("empresa", "negocio", "margem", "cliente", "operacao", "equipe", "tecnologia", "risco", "crescimento"),
            priority=4,
            public_safe=True,
            internal_only=False,
            synthesis_role="multidisciplinary_synthesis",
        ),
        AgentHook(
            hook_id="orkio.public_journey.synthesis",
            agent_id="orkio",
            family="journey",
            label="sintese publica do Orkio",
            description="Conduz a resposta final publica com Orkio como speaker unico.",
            triggers=("orkio", "me conduza", "como testar", "quero", "preciso", "ajuda"),
            priority=10,
            public_safe=True,
            internal_only=False,
            synthesis_role="public_synthesis",
        ),
        AgentHook(
            hook_id="orkio.visibility.public_guard",
            agent_id="orkio",
            family="guard",
            label="guarda de visibilidade publica",
            description="Garante que nomes internos nao virem resposta publica.",
            triggers=("chris", "orion", "cfo", "cto", "auditor", "planner", "quais agentes", "agentes especializados"),
            priority=1,
            public_safe=True,
            internal_only=False,
            synthesis_role="visibility_guard",
        ),
    ]


def advise(message: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return build_internal_advice(
        agent_id="orkio",
        message=message,
        profile=get_profile(),
        cards=get_knowledge_cards(),
        hooks=get_hooks(),
    )
