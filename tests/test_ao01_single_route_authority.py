from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
runtime_package = types.ModuleType("runtime")
runtime_package.__path__ = [str(ROOT / "runtime")]
sys.modules.setdefault("runtime", runtime_package)

cta_module = types.ModuleType("runtime.orkio_backend_cta_guard")
cta_module.enforce_backend_cta_policy = lambda payload: (payload, False)
sys.modules.setdefault("runtime.orkio_backend_cta_guard", cta_module)

guard_module = importlib.import_module("runtime.orkio_executive_guard")
stream_module = importlib.import_module("runtime.orkio_stream_precedence")

eos06_build_router_precedence_payload = (
    guard_module.eos06_build_router_precedence_payload
)
build_chat_stream_precedence_payload = (
    stream_module.build_chat_stream_precedence_payload
)


COMPLEX_PROMPTS = (
    """
Analise esta empresa SaaS B2B:
- MRR: R$ 480.000
- Margem bruta: 72%
- CAC: R$ 18.000
Entregue:
1. receita líquida;
2. LTV por duas metodologias;
3. relação LTV/CAC;
4. payback;
5. runway;
6. recomendação;
7. plano de ação para 90 dias.
Explique todas as fórmulas.
""",
    """
Compare três projetos e calcule VPL aproximado, retorno ajustado ao risco,
payback e análise de sensibilidade. Entregue recomendação final.
""",
    """
Audite este fluxo de chat e entregue:
1. estado real;
2. verde, amarelo e vermelho;
3. causa raiz;
4. patch mínimo;
5. rollback;
6. GO ou NO-GO.
""",
)


def test_complex_prompts_create_binding_full_runtime_decision() -> None:
    for prompt in COMPLEX_PROMPTS:
        guard = eos06_build_router_precedence_payload(prompt)
        assert guard["handled"] is False
        assert guard["category"] == "full_llm_runtime_required"

        route = build_chat_stream_precedence_payload({"message": prompt})
        assert route["handled"] is False
        assert route["route_family"] == "context_aware_llm_answer"
        assert route["force_full_llm_runtime"] is True
        assert route["block_executive_templates"] is True
        assert route["block_public_deterministic_fastpaths"] is True
        assert route["block_governed_evolution_fastpath"] is True
        assert route["guard_version"] == "AO01_EXECUTIVE_GUARD_COMPOUND_V3"
        assert route["guard_source_file"].endswith("orkio_executive_guard.py")
        assert len(route["guard_source_sha256"]) == 64


def test_simple_executive_prompt_keeps_template() -> None:
    route = build_chat_stream_precedence_payload(
        {"message": "Quais são os três principais riscos de uma empresa SaaS B2B?"}
    )
    assert route["handled"] is True
    assert route["route_family"] == "executive_strategy_answer"
    assert route.get("force_full_llm_runtime") is not True
