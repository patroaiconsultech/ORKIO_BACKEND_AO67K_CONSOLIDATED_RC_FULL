from __future__ import annotations

from typing import Any, Dict, Optional

from app.agents.base import AgentHook, build_internal_advice
from .knowledge import get_knowledge_cards
from .profile import get_profile


CHRIS_HOOKS_VERSION = "AO67C_CHRIS_HOOKS_V1"


def get_hooks() -> list[AgentHook]:
    return [
        AgentHook(
            hook_id="chris.internal.financial_strategy",
            agent_id="chris",
            family="specialist",
            label="análise financeira interna",
            description="Aconselha o Orkio sobre viabilidade financeira, custos, receita e margem.",
            triggers=("financeiro", "financeira", "análise financeira", "analise financeira", "finanças", "receita", "custos", "margem", "viabilidade", "payback", "valuation", "captação", "captacao"),
            priority=70,
            public_safe=False,
            internal_only=True,
            synthesis_role="internal_financial_advice",
        ),
        AgentHook(
            hook_id="chris.internal.business_strategy",
            agent_id="chris",
            family="specialist",
            label="estratégia de negócio interna",
            description="Aconselha o Orkio sobre modelo de negócio, mercado, canais, proposta de valor e crescimento.",
            triggers=("novo negócio", "novo negocio", "empreender", "modelo de negócio", "modelo de negocio", "vendas", "marketing", "clientes"),
            priority=71,
            public_safe=False,
            internal_only=True,
            synthesis_role="internal_business_advice",
        ),
    ]


def advise(message: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return build_internal_advice(
        agent_id="chris",
        message=message,
        profile=get_profile(),
        cards=get_knowledge_cards(),
        hooks=get_hooks(),
    )
