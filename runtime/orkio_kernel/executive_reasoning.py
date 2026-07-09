import re
import unicodedata

from .capability_resolver import summarize_capabilities


def _normalize(value: str) -> str:
    raw = str(value or "").strip().lower()
    try:
        raw = unicodedata.normalize("NFD", raw)
        raw = "".join(ch for ch in raw if unicodedata.category(ch) != "Mn")
    except Exception:
        pass
    return re.sub(r"\s+", " ", raw).strip()


def _parse_pt_number(raw: str) -> float:
    s = str(raw or "").strip().lower().replace("r$", "").replace(" ", "")
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        parts = s.split(".")
        if len(parts) > 1 and all(len(p) == 3 for p in parts[1:]):
            s = "".join(parts)
    try:
        return float(s)
    except Exception:
        return 0.0


def _money_matches(text: str):
    pattern = r"(?:r\$\s*)?(\d+(?:[\.,]\d+)?)\s*(m|mi|mm|milh(?:a|o|õ)es|milhoes|milhao|milhão|mil)?(?:/ano)?"
    values = []
    for m in re.finditer(pattern, str(text or ""), flags=re.IGNORECASE):
        full = str(m.group(0) or "")
        scale = _normalize(m.group(2) or "")
        if "r$" not in _normalize(full) and not scale:
            continue
        value = _parse_pt_number(m.group(1))
        if value <= 0:
            continue
        if scale in {"m", "mi", "mm"} or "milh" in scale or "milhao" in scale or "milhoes" in scale:
            value *= 1_000_000
        elif scale == "mil":
            value *= 1_000
        values.append((value, m.start(), m.end(), full))
    return values


def _nearest_keyword_value(values, text: str, keywords):
    low = _normalize(text)
    best = None
    best_score = 10**9
    for value, start, end, raw in values:
        window_start = max(0, start - 90)
        window = low[window_start:min(len(low), end + 90)]
        for keyword in keywords:
            normalized_keyword = _normalize(keyword)
            search_from = 0
            while True:
                pos = window.find(normalized_keyword, search_from)
                if pos < 0:
                    break
                absolute_pos = window_start + pos
                after_value_penalty = 500 if absolute_pos > start else 0
                score = abs(absolute_pos - start) + after_value_penalty
                if score < best_score:
                    best = value
                    best_score = score
                search_from = pos + len(normalized_keyword)
    return best


def _brl(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(value: float) -> str:
    return f"{value:.2f}%".replace(".", ",")


def build_quantitative_response(message: str) -> str:
    text = _normalize(message)
    money = _money_matches(message)
    revenue = _nearest_keyword_value(money, message, ("receita", "faturamento", "fatura"))
    operating_profit = _nearest_keyword_value(money, message, ("lucro operacional", "lucro", "resultado operacional"))

    if revenue is None and money:
        revenue = money[0][0]
    if operating_profit is None and len(money) >= 2 and ("lucro" in text or "resultado operacional" in text):
        operating_profit = money[1][0]

    if revenue and operating_profit is not None and ("margem" in text or "lucro operacional" in text):
        margin = (float(operating_profit) / float(revenue) * 100.0) if revenue else 0.0
        return (
            "Cálculo objetivo.\n\n"
            "Fórmula:\n"
            "- margem operacional = lucro operacional ÷ receita\n\n"
            "Aplicação:\n"
            f"- receita: {_brl(float(revenue))}\n"
            f"- lucro operacional: {_brl(float(operating_profit))}\n"
            f"- margem operacional: {_brl(float(operating_profit))} ÷ {_brl(float(revenue))} = {_pct(margin)}\n\n"
            f"Veredito matemático: a margem operacional informada é {_pct(margin)}. "
            "A conta usa somente os números fornecidos."
        )

    return (
        "Posso calcular, mas preciso da fórmula desejada e dos valores necessários. "
        "Números de contexto, como faturamento ou número de funcionários, não são tratados como cálculo sem pedido explícito."
    )


def build_executive_strategy_response(message: str) -> str:
    text = _normalize(message)

    if any(marker in text for marker in ("competitivo", "concorrencia", "players", "tendencias", "diferenciar")):
        return (
            "Diagnóstico breve: esta é uma decisão de posicionamento competitivo, não um cálculo financeiro.\n\n"
            "1. Campo competitivo\n"
            "- Sinal de alerta: comparar apenas preço e ignorar canal, ICP, implementação e retenção.\n"
            "- Ação recomendada: separar concorrentes diretos, substitutos manuais e soluções enterprise que descem para PME.\n\n"
            "2. Tendências de pressão\n"
            "- Sinal de alerta: IA, embedded finance, open finance e automação reduzindo diferenciais superficiais.\n"
            "- Ação recomendada: medir onde sua solução reduz tempo, risco e custo operacional para o cliente.\n\n"
            "3. Diferenciação defensável\n"
            "- Sinal de alerta: discurso amplo demais, sem prova de valor por segmento.\n"
            "- Ação recomendada: escolher um ICP prioritário e provar ganho em onboarding, fechamento contábil, cobrança, caixa ou decisão financeira.\n\n"
            "Próximo passo sugerido: montar uma matriz com players, ICP atendido, promessa central, pricing, canal e prova de ROI."
        )

    if "retencao" in text or "priorizar" in text:
        return (
            "Diagnóstico breve: há números no contexto, mas a pergunta pede escolha estratégica, não cálculo.\n\n"
            "Prioridades e trade-offs:\n"
            "1. Retenção protege receita, aprendizado do cliente e previsibilidade.\n"
            "2. Expansão internacional aumenta opcionalidade, mas adiciona complexidade comercial, jurídica e operacional.\n"
            "3. A decisão depende de repetibilidade: ICP claro, churn controlado, payback previsível e liderança com foco.\n\n"
            "Sinais de alerta: churn crescendo, pipeline local fraco, suporte saturado ou liderança dispersa.\n\n"
            "Ação recomendada: priorizar retenção se a base ainda não é previsível; testar expansão com aposta limitada se a máquina local já for repetível.\n\n"
            "Próximo passo sugerido: montar uma matriz de decisão com impacto, risco, prazo e capacidade interna."
        )

    if any(marker in text for marker in ("internacional", "internacionalizacao", "mexico", "mercado mexicano", "expandir")):
        return (
            "Diagnóstico breve: há números no contexto, mas a pergunta pede framework de decisão estratégica, não cálculo financeiro.\n\n"
            "1. Atratividade do mercado: TAM/SAM realista, dor local, concorrentes e disposição de pagamento.\n"
            "2. Prontidão operacional: suporte, idioma, compliance, billing, integrações e implantação remota.\n"
            "3. Estratégia de entrada: piloto com parceiros, venda direta, canal local ou expansão por clientes multinacionais.\n"
            "4. Risco financeiro e foco: orçamento máximo, hipótese de payback, métricas de tração e ponto de parada.\n\n"
            "Sinais de alerta: churn local ainda alto, ICP indefinido, liderança sem folga ou customizações pesadas.\n\n"
            "Próximo passo sugerido: aprovar um piloto limitado com critérios de go/no-go antes de comprometer expansão ampla."
        )

    return (
        "Diagnóstico breve: esta é uma pergunta executiva aberta. Vou tratar como decisão estratégica, não como cálculo financeiro.\n\n"
        "1. Risco de crescimento com eficiência\n"
        "- Sinal de alerta: CAC subindo, churn estável ou expansão abaixo do esperado.\n"
        "- Ação recomendada: revisar ICP, payback e eficiência comercial.\n\n"
        "2. Risco de concentração de receita\n"
        "- Sinal de alerta: dependência excessiva de poucos clientes, canais ou segmentos.\n"
        "- Ação recomendada: mapear concentração e criar plano de diversificação.\n\n"
        "3. Risco de execução organizacional\n"
        "- Sinal de alerta: liderança sobrecarregada, gaps de gestão ou lentidão em produto.\n"
        "- Ação recomendada: definir cadência executiva, ownership e métricas semanais.\n\n"
        "Próximo passo sugerido: transformar estes riscos em um plano de ação de 30/60/90 dias."
    )


def build_executive_crisis_response(message: str) -> str:
    return (
        "Diagnóstico breve: isto é uma crise executiva de continuidade comercial. A prioridade é proteger clientes, pipeline e moral do time antes de discutir qualquer projeto novo.\n\n"
        "Próximas 72 horas:\n"
        "1. Estabilizar comando: nomeie um responsável interino por vendas ainda hoje.\n"
        "2. Proteger pipeline: classifique oportunidades por valor, data de fechamento, decisor e risco de perda.\n"
        "3. Blindar clientes-chave: defina quem falará com cada conta crítica e prepare mensagem de continuidade.\n"
        "4. Preservar informação: centralize CRM, forecast, playbooks, propostas, acordos pendentes e histórico de negociação.\n"
        "5. Reorganizar cadência: faça checkpoint diário por 2 semanas com funil, riscos, decisões e donos.\n\n"
        "Sinais de alerta: vendedores sem direção, forecast opaco, clientes-chave inseguros ou propostas paradas sem owner.\n\n"
        "Próximo passo sugerido: fazer hoje uma reunião de 30 minutos com liderança e donos do pipeline para redistribuir contas e próximos contatos."
    )


def build_executive_dashboard_response(message: str) -> str:
    return (
        "Diagnóstico breve: para CEO de SaaS B2B em estágio Series A, o dashboard semanal deve conectar crescimento, eficiência, retenção e execução.\n\n"
        "KPIs recomendados:\n"
        "1. Receita: MRR/ARR, new MRR, expansion MRR, contraction MRR e churn MRR.\n"
        "2. Comercial: pipeline qualificado, cobertura de pipeline, win rate, ciclo de venda, CAC e payback.\n"
        "3. Cliente: logo churn, NRR, ativação, uso do produto, health score e tickets críticos.\n"
        "4. Produto: entregas-chave, bugs críticos, tempo até valor e adoção de features essenciais.\n"
        "5. Execução: prioridades da semana, owners, bloqueios, decisões pendentes e capacidade do time.\n\n"
        "Sinais de alerta: crescimento sem retenção, pipeline inflado, CAC subindo, NRR abaixo do esperado ou time sem owners claros.\n\n"
        "Próximo passo sugerido: criar uma reunião semanal de 45 minutos em que cada desvio tenha decisão, responsável e prazo."
    )


def build_governance_response() -> str:
    return (
        "Proposta em observe_only / proposal_only=true.\n\n"
        "1. Estado comprovado\n"
        "- Há uma solicitação para propor evolução estrutural.\n"
        "- Nenhuma execução, escrita, branch, PR ou deploy será feita nesta resposta.\n\n"
        "2. Capacidade declarada\n"
        "- A plataforma possui base de governança, runtime de chat, propostas e aprovação humana.\n"
        "- Declaração de capacidade não prova disponibilidade operacional em tempo real.\n\n"
        "3. Validação pendente\n"
        "- Validar logs recentes do stream.\n"
        "- Confirmar persistência única por trace_id/thread_id/message_id.\n"
        "- Confirmar emissão de done e liberação do input.\n\n"
        "4. Evolução proposta\n"
        "- Consolidar o Orkio Kernel como ponto único de decisão cognitiva.\n"
        "- Manter Runtime apenas para transporte, persistência e encerramento.\n\n"
        "5. Impacto\n"
        "- Reduz acoplamento no main.py.\n"
        "- Diminui respostas duplicadas e conflitos de roteamento.\n\n"
        "6. Riscos\n"
        "- Risco médio por alterar precedência lógica.\n"
        "- Exige smokes de regressão.\n\n"
        "7. Validação\n"
        "- Uma mensagem deve gerar uma resposta, uma persistência e um done.\n"
        "- Perguntas de capacidade devem separar produção, beta, roadmap e proposta.\n\n"
        "8. Rollback\n"
        "- Desativar hook do Kernel e restaurar fluxo anterior.\n\n"
        "9. Aprovação humana\n"
        "- Obrigatória antes de qualquer merge, PR, deploy ou escrita automatizada.\n\n"
        "Governança: mode=observe_only; proposal_only=true; write_executed=false; "
        "branch_created=false; pr_created=false; deploy_executed=false; human_approval_required=true."
    )


def build_capability_response(registry=None) -> str:
    return (
        "Estado das capacidades do Orkio, usando o Capability Registry.\n\n"
        f"{summarize_capabilities(registry)}\n\n"
        "Regra: funcionalidades em roadmap ou proposal não devem ser apresentadas como produção."
    )


def build_autoevolution_boundary_response() -> str:
    return (
        "Capacidade de autoevolução — separação operacional.\n\n"
        "Capacidade declarada:\n"
        "- A arquitetura prevê proposta de mudanças, revisão, diff, rollback e aprovação humana.\n\n"
        "Disponibilidade real:\n"
        "- Nesta resposta não há comprovação de execução real de código, criação de PR ou deploy.\n\n"
        "Limites:\n"
        "- Não devo afirmar que altero código, abro PR ou faço deploy sozinho em produção.\n\n"
        "Aprovação humana:\n"
        "- Obrigatória antes de qualquer escrita, branch, PR, merge ou deploy.\n\n"
        "Veredito: posso propor e estruturar; execução real deve permanecer governada."
    )
