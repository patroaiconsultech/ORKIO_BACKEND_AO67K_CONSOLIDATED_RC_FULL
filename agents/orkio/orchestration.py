"""
EO-06 — Multi-Agent Orchestration.

Planeja orquestração sem inventar agentes e sem executar delegações.
"""

from typing import Dict, List


KNOWN_AGENT_IDS = {"Orkio", "Orion", "Chris"}


def build_orchestration_plan(request: str, available_agents: List[str] | None = None) -> Dict[str, object]:
    available = set(available_agents or []) or KNOWN_AGENT_IDS
    text = (request or "").lower()
    suggested: list[str] = []

    if any(k in text for k in ["backend", "bug", "logs", "api", "deploy"]):
        if "Orion" in available:
            suggested.append("Orion")
    if any(k in text for k in ["negócio", "estratégia", "valuation", "mercado"]):
        if "Chris" in available:
            suggested.append("Chris")

    return {
        "mode": "observe_only",
        "delegation_executed": False,
        "available_agents": sorted(available),
        "suggested_agents": suggested,
        "rule": "Não inventar agentes. Delegação real exige disponibilidade confirmada e aprovação humana.",
    }
