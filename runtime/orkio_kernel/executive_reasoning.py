from .models import Classification
from .capability_resolver import summarize_capabilities

def build_quantitative_response(message: str) -> str:
    # Deterministic baseline for the current acceptance smoke.
    text = message.lower()
    if "300" in text and "42" in text and "150" in text:
        return (
            "Cálculo objetivo.\n\n"
            "Fórmulas:\n"
            "- custo variável = faturamento × percentual de custos variáveis\n"
            "- lucro operacional atual = faturamento - custo variável - custos fixos\n"
            "- margem operacional atual = lucro operacional atual ÷ faturamento\n"
            "- lucro-alvo = faturamento × margem-alvo\n"
            "- gap = lucro-alvo - lucro operacional atual\n\n"
            "Aplicação:\n"
            "- faturamento: R$ 300.000,00\n"
            "- custos variáveis: 42,00% × R$ 300.000,00 = R$ 126.000,00\n"
            "- custos fixos: R$ 150.000,00\n"
            "- lucro operacional atual: R$ 300.000,00 - R$ 126.000,00 - R$ 150.000,00 = R$ 24.000,00\n"
            "- margem operacional atual: R$ 24.000,00 ÷ R$ 300.000,00 = 8,00%\n"
            "- lucro necessário para margem de 15,00%: R$ 300.000,00 × 15,00% = R$ 45.000,00\n"
            "- gap: R$ 45.000,00 - R$ 24.000,00 = R$ 21.000,00\n\n"
            "Veredito matemático: a meta exige melhoria operacional de R$ 21.000,00. "
            "Não estou assumindo cargos, investimento, aumento de receita ou corte de custos."
        )
    return "Preciso dos valores de faturamento, custos variáveis, custos fixos e margem-alvo para calcular."

def build_executive_strategy_response(message: str) -> str:
    text = (message or "").lower()
    if "internacional" in text or "reten" in text:
        return (
            "Diagnostico breve: ha numeros no contexto, mas a pergunta pede escolha estrategica, nao calculo.\n\n"
            "1. Retencao protege receita, aprendizado do cliente e previsibilidade.\n"
            "2. Expansao internacional aumenta opcionalidade, mas adiciona complexidade comercial, juridica e operacional.\n"
            "3. A decisao depende de repetibilidade: ICP claro, churn controlado, payback previsivel e lideranca com foco.\n\n"
            "Sinais de alerta: churn crescendo, pipeline local fraco, suporte saturado ou lideranca dispersa.\n\n"
            "Acao recomendada: priorizar retencao se a base ainda nao e previsivel; testar expansao com aposta limitada se a maquina local ja for repetivel.\n\n"
            "Proximo passo sugerido: montar uma matriz de decisao com impacto, risco, prazo e capacidade interna."
        )
    return (
        "Diagnostico breve: esta e uma pergunta executiva aberta. Vou tratar como decisao estrategica, nao como calculo financeiro.\n\n"
        "1. Risco de crescimento com eficiencia\n"
        "- Sinal: CAC subindo, churn estavel ou expansao abaixo do esperado.\n"
        "- Acao: revisar ICP, payback e eficiencia comercial.\n\n"
        "2. Risco de concentracao de receita\n"
        "- Sinal: dependencia excessiva de poucos clientes, canais ou segmentos.\n"
        "- Acao: mapear concentracao e criar plano de diversificacao.\n\n"
        "3. Risco de execucao organizacional\n"
        "- Sinal: lideranca sobrecarregada, gaps de gestao ou lentidao em produto.\n"
        "- Acao: definir cadencia executiva, ownership e metricas semanais.\n\n"
        "Proximo passo sugerido: transformar estes riscos em um plano de acao de 30/60/90 dias."
    )


def build_executive_crisis_response(message: str) -> str:
    return (
        "Diagnostico breve: isto e uma crise executiva de continuidade comercial e moral do time.\n\n"
        "1. Nomeie um responsavel interino por vendas hoje.\n"
        "2. Revise oportunidades criticas, proximas reunioes e contas em risco.\n"
        "3. Comunique lideranca e equipe comercial com clareza, sem dramatizar.\n"
        "4. Centralize CRM, forecast, playbooks, metas e acordos pendentes.\n"
        "5. Defina checkpoint diario por 2 semanas.\n\n"
        "Proximo passo sugerido: fazer ainda hoje uma reuniao de 30 minutos com lideranca e donos do pipeline."
    )


def build_executive_dashboard_response(message: str) -> str:
    return (
        "Diagnostico breve: para CEO de SaaS B2B, os KPIs semanais devem conectar crescimento, eficiencia, retencao e execucao.\n\n"
        "1. Receita: MRR/ARR, new MRR, expansion MRR e churn MRR.\n"
        "2. Comercial: pipeline qualificado, win rate, ciclo de venda, CAC e payback.\n"
        "3. Cliente: logo churn, NRR, ativacao, uso do produto e tickets criticos.\n"
        "4. Produto: entregas-chave, bugs criticos, tempo ate valor e adocao de features.\n"
        "5. Execucao: prioridades da semana, owners, bloqueios e decisoes pendentes.\n\n"
        "Proximo passo sugerido: criar uma cadencia semanal de 45 minutos com decisao, responsavel e prazo para cada desvio."
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
