"""
EO-08 — Executive Communication.

Formatação padronizada para respostas do Orkio.
"""

from typing import Iterable


def _bullets(items: Iterable[str]) -> str:
    return "\n".join(f"- {x}" for x in items if x)


def format_executive_response(
    *,
    objective: str,
    proven: list[str] | None = None,
    available: list[str] | None = None,
    roadmap: list[str] | None = None,
    risks: list[str] | None = None,
    recommendation: str | None = None,
    governance: dict | None = None,
) -> str:
    parts = [objective.strip()]
    if proven:
        parts += ["\nEstado comprovado:", _bullets(proven)]
    if available:
        parts += ["\nDisponível agora:", _bullets(available)]
    if roadmap:
        parts += ["\nRoadmap/proposta:", _bullets(roadmap)]
    if risks:
        parts += ["\nRiscos:", _bullets(risks)]
    if recommendation:
        parts += ["\nRecomendação:", recommendation.strip()]
    if governance:
        parts += [
            "\nGovernança:",
            _bullets([f"{k}: {v}" for k, v in governance.items()]),
        ]
    return "\n".join(parts).strip()
