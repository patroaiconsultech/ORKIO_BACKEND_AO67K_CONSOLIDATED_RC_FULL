import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

agent_access_policy = types.ModuleType("app.services.agent_access_policy")
agent_access_policy.is_public_internal_agent_request = lambda value: False
agent_access_policy.public_agent_access_denied_answer = lambda: "denied"
agent_access_policy.public_agent_catalog_answer = lambda: "catalog"
sys.modules["app.services.agent_access_policy"] = agent_access_policy

from runtime import amcham_public_journey_policy as MODULE


SAAS_BOARD_PROMPT = (
    "Atue como um grande executivo e conselheiro de conselho. Avalie uma empresa SaaS B2B "
    "com MRR de R$ 800 mil, margem bruta de 72%, despesas fixas de R$ 510 mil/mes, "
    "churn mensal de 3,2%, CAC de R$ 18 mil, ticket medio mensal de R$ 6 mil e caixa "
    "de R$ 1,8 milhao. O board quer crescer 35% em 12 meses sem captacao. Entregue: "
    "calculos corretos de lucro operacional, margem operacional, runway se aplicavel, "
    "LTV simplificado e LTV/CAC; 3 restricoes criticas; plano 30-60-90 dias com donos, "
    "KPIs, riscos e gatilhos de parada; separe fatos, inferencias e dados faltantes. "
    "Seja direto e nao invente dados."
)


decision = MODULE.build_amcham_public_journey_decision(SAAS_BOARD_PROMPT)
assert decision["handled"] is False, decision
assert decision["reason"] == "structured_executive_task_direct_answer", decision
assert decision["policy_version"] == MODULE.STRUCTURED_EXECUTIVE_TASK_POLICY_VERSION, decision


generic = MODULE.build_amcham_public_journey_decision(
    "Quero fazer um diagnostico do meu projeto, por onde comeco?"
)
assert generic["handled"] is True, generic
assert generic["public_intent"] == "business_or_project_diagnostic", generic


print("AO69B_STRUCTURED_EXECUTIVE_TASK_BYPASS_PASS")
