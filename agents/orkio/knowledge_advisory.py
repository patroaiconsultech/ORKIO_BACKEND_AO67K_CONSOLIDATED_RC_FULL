from __future__ import annotations

from app.agents.base import KnowledgeCard


ORKIO_ADVISORY_KNOWLEDGE_VERSION = "AO83_ORKIO_WORLD_CLASS_ADVISOR_V1"


def get_advisory_knowledge_cards() -> list[KnowledgeCard]:
    return [
        KnowledgeCard(
            card_id="orkio.advisory.executive_diagnosis",
            agent_id="orkio",
            title="Diagnostico executivo e decisao",
            summary=(
                "Comece pelo objetivo, decisao, contexto, restricoes, stakeholders, urgencia e metrica de sucesso. "
                "Separe fatos, hipoteses, inferencias e lacunas; encontre causa raiz, explicite tradeoffs, recomende uma posicao "
                "e termine com a menor proxima acao de alta alavancagem."
            ),
            domains=("executive_advisory", "diagnosis", "decision_science", "strategy"),
            triggers=("diagnostico", "decisao", "estrategia", "prioridade", "problema", "objetivo", "recomende", "o que fazer", "primeiro passo"),
            public_safe=True,
            internal_only=False,
            priority=2,
        ),
        KnowledgeCard(
            card_id="orkio.advisory.roadmap_execution",
            agent_id="orkio",
            title="Roadmaps e execucao",
            summary=(
                "Transforme objetivos em fases ordenadas com resultado esperado, workstreams, responsavel, entregavel, dependencia, "
                "marco, KPI, risco e gate de decisao. Use Agora/Depois/Mais tarde ou 30/60/90 dias conforme o horizonte; "
                "diferencie atividade de resultado e mantenha um backlog explicitamente fora de escopo."
            ),
            domains=("roadmap", "execution", "portfolio", "project_management", "transformation"),
            triggers=("roadmap", "plano de acao", "cronograma", "30 60 90", "implementar", "execucao", "projeto", "priorizar", "etapas"),
            public_safe=True,
            internal_only=False,
            priority=3,
        ),
        KnowledgeCard(
            card_id="orkio.advisory.finance_margin_value",
            agent_id="orkio",
            title="Financas, margem e criacao de valor",
            summary=(
                "Analise receita, preco, mix, volume, custo variavel, capacidade, utilizacao, custo de servir, CAC, retencao, caixa e capital. "
                "Para margem em servicos, comece medindo rentabilidade por cliente, oferta e projeto com horas/capacidade e custos corretamente alocados; "
                "depois ataque precificacao, escopo, produtividade, mix e vazamentos. Declare premissas e use cenarios."
            ),
            domains=("finance", "margin", "pricing", "unit_economics", "valuation", "cash_flow"),
            triggers=("margem", "rentabilidade", "preco", "precificacao", "custos", "caixa", "valuation", "roi", "receita", "lucro", "ebitda"),
            public_safe=True,
            internal_only=False,
            priority=4,
        ),
        KnowledgeCard(
            card_id="orkio.advisory.customer_growth_commercial",
            agent_id="orkio",
            title="Cliente, crescimento e comercial",
            summary=(
                "Conecte segmento, problema valioso, proposta de valor, jornada, aquisicao, conversao, onboarding, adocao, retencao e expansao. "
                "Diagnostique o funil com taxas e coortes antes de prescrever campanhas; alinhe ICP, oferta, canal, prova, vendas e customer success."
            ),
            domains=("customer", "growth", "sales", "marketing", "customer_success"),
            triggers=("cliente", "vendas", "comercial", "marketing", "crescimento", "funil", "conversao", "retencao", "churn", "proposta de valor", "go to market"),
            public_safe=True,
            internal_only=False,
            priority=5,
        ),
        KnowledgeCard(
            card_id="orkio.advisory.operations_people_change",
            agent_id="orkio",
            title="Operacoes, processos, pessoas e mudanca",
            summary=(
                "Mapeie fluxo de valor, demanda, capacidade, gargalo, variabilidade, retrabalho, qualidade, controles e nivel de servico. "
                "Defina dono do processo e indicadores; em mudancas, alinhe patrocinio, papeis, competencias, incentivos, comunicacao, adocao e rituais de gestao."
            ),
            domains=("operations", "process", "people", "change_management", "quality"),
            triggers=("operacao", "processo", "gargalo", "produtividade", "eficiencia", "equipe", "pessoas", "mudanca", "capacidade", "qualidade"),
            public_safe=True,
            internal_only=False,
            priority=6,
        ),
        KnowledgeCard(
            card_id="orkio.advisory.product_technology_ai",
            agent_id="orkio",
            title="Produto, tecnologia, dados e IA",
            summary=(
                "Parta do problema e do resultado do usuario, nao da tecnologia. Defina caso de uso, baseline, dados, riscos, arquitetura proporcional, "
                "experimento, criterios de sucesso, operacao e governanca. Em IA, avalie qualidade, privacidade, seguranca, custo, latencia, supervisao humana e monitoramento."
            ),
            domains=("product", "technology", "data", "ai", "cybersecurity"),
            triggers=("produto", "tecnologia", "software", "dados", "ia", "inteligencia artificial", "automacao", "arquitetura", "seguranca", "mvp"),
            public_safe=True,
            internal_only=False,
            priority=7,
        ),
        KnowledgeCard(
            card_id="orkio.advisory.governance_risk_esg",
            agent_id="orkio",
            title="Governanca, risco, compliance e ESG",
            summary=(
                "Identifique obrigacoes, materialidade, impacto, probabilidade, controles, owner, evidencia e risco residual. "
                "Em ESG, evite slogans: conecte temas materiais a estrategia, operacao, stakeholders, metas, indicadores, governanca e divulgacao verificavel. "
                "Assuntos juridicos e regulados exigem validacao profissional e fontes atuais."
            ),
            domains=("governance", "risk", "compliance", "esg", "legal"),
            triggers=("governanca", "risco", "compliance", "esg", "sustentabilidade", "regulacao", "juridico", "controle", "auditoria"),
            public_safe=True,
            internal_only=False,
            priority=8,
        ),
        KnowledgeCard(
            card_id="orkio.advisory.research_epistemics",
            agent_id="orkio",
            title="Pesquisa, evidencia e honestidade epistemica",
            summary=(
                "Nao trate memoria do modelo como fonte atual. Para fatos recentes, nichados ou de alto impacto, verifique fontes autorizadas e cite-as quando disponiveis. "
                "Diferencie evidencia de hipotese, indique confianca e lacunas, nao invente numeros e diga exatamente o que precisa ser validado."
            ),
            domains=("research", "evidence", "critical_thinking", "knowledge"),
            triggers=("pesquise", "fonte", "evidencia", "dados atuais", "mercado", "benchmark", "tendencia", "lei", "regulacao", "confirme"),
            public_safe=True,
            internal_only=False,
            priority=9,
        ),
    ]
