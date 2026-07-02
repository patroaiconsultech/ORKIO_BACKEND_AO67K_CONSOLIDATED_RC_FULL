import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "runtime" / "orkio_executive_guard.py"
SPEC = importlib.util.spec_from_file_location("orkio_executive_guard", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
classify_orkio_executive_request = MODULE.classify_orkio_executive_request


MUST_REACH_RUNTIME = (
    "Minha empresa fatura R$ 300 mil por mes e lucra R$ 24 mil. Calcule a margem atual e o gap para 15%.",
    "Faca um diagnostico da minha empresa B2B e recomende o primeiro passo.",
    "Crie um roadmap de 90 dias com metas, responsaveis, KPIs e riscos.",
    "Margem 8%, meta 15%: mostre os calculos e proponha cenarios.",
    "Prepare minha empresa para captacao e identifique os riscos.",
    "Responda apenas com a decisao e o proximo passo.",
)

MAY_USE_FASTPATH = (
    "Oi",
    "Bom dia",
    "Quem e o Orkio?",
    "Qual e o status do sistema?",
)

for prompt in MUST_REACH_RUNTIME:
    decision = classify_orkio_executive_request(prompt)
    assert decision["force_context_runtime"] is True, (prompt, decision)

for prompt in MAY_USE_FASTPATH:
    decision = classify_orkio_executive_request(prompt)
    assert decision["force_context_runtime"] is False, (prompt, decision)

print("AO85_ORKIO_EXECUTIVE_GUARD_PASS")
