"""
EO-02 — Executive Reasoning.

Monta uma moldura de raciocínio padronizada para respostas executivas.
"""

from typing import Any, Dict, List


def build_reasoning_frame(
    *,
    proven_state: List[str] | None = None,
    available_capabilities: List[str] | None = None,
    declared_capabilities: List[str] | None = None,
    pending_validation: List[str] | None = None,
    risks: List[str] | None = None,
    recommendation: str | None = None,
    next_step: str | None = None,
) -> Dict[str, Any]:
    return {
        "estado_comprovado": proven_state or [],
        "capacidades_disponiveis": available_capabilities or [],
        "capacidades_declaradas": declared_capabilities or [],
        "validacao_pendente": pending_validation or [],
        "riscos": risks or [],
        "recomendacao": recommendation or "",
        "proximo_passo": next_step or "",
    }


def compact_frame_for_public_answer(frame: Dict[str, Any]) -> str:
    sections = [
        ("Estado comprovado", frame.get("estado_comprovado", [])),
        ("Capacidades disponíveis", frame.get("capacidades_disponiveis", [])),
        ("Capacidades declaradas", frame.get("capacidades_declaradas", [])),
        ("Validação pendente", frame.get("validacao_pendente", [])),
        ("Riscos", frame.get("riscos", [])),
    ]
    out: list[str] = []
    for title, values in sections:
        if values:
            out.append(f"{title}:")
            out.extend([f"- {v}" for v in values])
    if frame.get("recomendacao"):
        out.append(f"Recomendação: {frame['recomendacao']}")
    if frame.get("proximo_passo"):
        out.append(f"Próximo passo: {frame['proximo_passo']}")
    return "\n".join(out)
