"""
EO-07 — Truth Engine.

Classifica afirmações e capacidades em níveis de verdade operacional.
"""

from enum import Enum
from typing import Any, Dict


class TruthLevel(str, Enum):
    PROVEN = "estado_comprovado"
    AVAILABLE = "capacidade_disponivel"
    BETA = "beta"
    ROADMAP = "roadmap"
    PROPOSAL = "proposta"
    HYPOTHESIS = "hipotese"
    UNKNOWN = "desconhecido"


_STATUS_MAP = {
    "production": TruthLevel.AVAILABLE,
    "available": TruthLevel.AVAILABLE,
    "producao": TruthLevel.AVAILABLE,
    "prod": TruthLevel.AVAILABLE,
    "beta": TruthLevel.BETA,
    "roadmap": TruthLevel.ROADMAP,
    "planned": TruthLevel.ROADMAP,
    "proposal": TruthLevel.PROPOSAL,
    "proposta": TruthLevel.PROPOSAL,
    "concept": TruthLevel.HYPOTHESIS,
    "hypothesis": TruthLevel.HYPOTHESIS,
    "unknown": TruthLevel.UNKNOWN,
}


def classify_truth_level(item: Dict[str, Any] | str | None) -> TruthLevel:
    if item is None:
        return TruthLevel.UNKNOWN
    if isinstance(item, str):
        return _STATUS_MAP.get(item.strip().lower(), TruthLevel.UNKNOWN)
    status = str(item.get("status", "")).strip().lower()
    if item.get("proven") is True:
        return TruthLevel.PROVEN
    return _STATUS_MAP.get(status, TruthLevel.UNKNOWN)


def must_disclaim(level: TruthLevel) -> bool:
    return level in {
        TruthLevel.BETA,
        TruthLevel.ROADMAP,
        TruthLevel.PROPOSAL,
        TruthLevel.HYPOTHESIS,
        TruthLevel.UNKNOWN,
    }


def label_for(level: TruthLevel) -> str:
    return {
        TruthLevel.PROVEN: "Estado comprovado",
        TruthLevel.AVAILABLE: "Disponível agora",
        TruthLevel.BETA: "Beta",
        TruthLevel.ROADMAP: "Roadmap",
        TruthLevel.PROPOSAL: "Proposta",
        TruthLevel.HYPOTHESIS: "Hipótese",
        TruthLevel.UNKNOWN: "Não confirmado",
    }[level]
