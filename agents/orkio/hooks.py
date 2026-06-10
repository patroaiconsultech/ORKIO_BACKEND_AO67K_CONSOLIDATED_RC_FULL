from __future__ import annotations

from typing import Any, Dict, Optional

from app.agents.base import AgentHook, build_internal_advice
from .knowledge import get_knowledge_cards
from .profile import get_profile


ORKIO_HOOKS_VERSION = "AO67C_ORKIO_HOOKS_V1"


def get_hooks() -> list[AgentHook]:
    return [
        AgentHook(
            hook_id="orkio.public_journey.synthesis",
            agent_id="orkio",
            family="journey",
            label="síntese pública do Orkio",
            description="Conduz a resposta final pública com Orkio como speaker único.",
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
            label="guarda de visibilidade pública",
            description="Garante que nomes internos não virem resposta pública.",
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
