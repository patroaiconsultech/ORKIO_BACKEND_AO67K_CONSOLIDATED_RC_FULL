"""
Runtime bridge — ORKIO Executive Cognitive System RC-1.

Este arquivo é propositalmente seguro:
- sem rede;
- sem banco;
- sem alteração de stream;
- sem execução de patch;
- sem deploy.

Pode ser importado pelo main.py futuramente.
"""

from typing import Dict

from agents.orkio.capability_resolver import CapabilityResolver
from agents.orkio.decision_engine import classify_intent
from agents.orkio.identity import ORKIO_IDENTITY
from agents.orkio.communication import format_executive_response


def answer_platform_capability_question(message: str) -> Dict[str, object]:
    resolver = CapabilityResolver()
    return {
        "handled": True,
        "route_family": "orkio_executive_cognitive_system_rc1",
        "category": "platform_capability",
        "answer": (
            "A plataforma ORKIO deve ser explicada separando o que está disponível agora, "
            "o que está em beta, o que está em roadmap e o que é apenas proposta.\n\n"
            + resolver.status_summary()
        ),
        "governance": ORKIO_IDENTITY["default_governance"],
    }


def build_orkio_executive_answer(message: str) -> Dict[str, object]:
    intent = classify_intent(message)
    if intent["intent"] == "platform_capability":
        return answer_platform_capability_question(message)

    return {
        "handled": False,
        "route_family": "orkio_executive_cognitive_system_rc1",
        "category": intent["intent"],
        "confidence": intent["confidence"],
        "governance": ORKIO_IDENTITY["default_governance"],
    }


def executive_system_smoke() -> str:
    answer = build_orkio_executive_answer("O que a plataforma Orkio faz hoje e o que está no roadmap?")
    assert answer["handled"] is True
    assert "Disponível agora" in answer["answer"]
    assert "Roadmap" in answer["answer"]
    return "ORKIO_EXECUTIVE_COGNITIVE_SYSTEM_RC1_OK"
