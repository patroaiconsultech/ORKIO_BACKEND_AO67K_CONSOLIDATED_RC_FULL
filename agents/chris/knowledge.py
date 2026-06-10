from __future__ import annotations

from app.agents.base import KnowledgeCard


CHRIS_KNOWLEDGE_VERSION = "AO67C_CHRIS_KNOWLEDGE_V1"


def get_knowledge_cards() -> list[KnowledgeCard]:
    return [
        KnowledgeCard(
            card_id="chris.finance.viability",
            agent_id="chris",
            title="Viabilidade financeira",
            summary=(
                "Sinal interno para organizar receita, custos, margem, ticket médio, payback, riscos financeiros e hipóteses críticas."
            ),
            domains=("finance", "viability", "business"),
            triggers=("financeiro", "financeira", "análise financeira", "analise financeira", "finanças", "financas", "viabilidade", "receita", "custos", "margem", "payback", "ticket médio", "ticket medio"),
            public_safe=False,
            internal_only=True,
            priority=30,
        ),
        KnowledgeCard(
            card_id="chris.business.model",
            agent_id="chris",
            title="Modelo de negócio",
            summary=(
                "Sinal interno para estruturar problema, público, proposta de valor, canais, monetização e operação."
            ),
            domains=("business_model", "strategy", "entrepreneurship"),
            triggers=("modelo de negócio", "modelo de negocio", "novo negócio", "novo negocio", "empreender", "startup", "proposta de valor"),
            public_safe=False,
            internal_only=True,
            priority=31,
        ),
        KnowledgeCard(
            card_id="chris.growth.market",
            agent_id="chris",
            title="Go-to-market e crescimento",
            summary=(
                "Sinal interno para mapear público-alvo, canais, relacionamento, vendas, posicionamento e primeiras validações."
            ),
            domains=("growth", "sales", "market"),
            triggers=("vendas", "marketing", "growth", "go to market", "go-to-market", "clientes", "mercado", "público alvo", "publico alvo"),
            public_safe=False,
            internal_only=True,
            priority=32,
        ),
        KnowledgeCard(
            card_id="chris.executive.risk",
            agent_id="chris",
            title="Risco executivo de negócio",
            summary=(
                "Sinal interno para avaliar riscos comerciais, operacionais, financeiros e de execução, sem expor agente financeiro ao público."
            ),
            domains=("risk", "governance", "business"),
            triggers=("risco", "riscos", "governança", "governanca", "compliance", "execução", "execucao", "prioridade"),
            public_safe=False,
            internal_only=True,
            priority=33,
        ),
    ]
