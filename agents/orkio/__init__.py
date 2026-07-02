"""
ORKIO Executive Cognitive System RC-1.

Módulos puros, sem efeitos colaterais, para elevar o Orkio a um agente executivo
com identidade, raciocínio, verdade operacional e governança.

RC-1 não altera banco, deploy, SSE nem frontend.
"""
from .identity import ORKIO_IDENTITY
from .reasoning import build_reasoning_frame
from .truth_engine import classify_truth_level, TruthLevel
from .capability_resolver import CapabilityResolver
from .decision_engine import classify_intent
from .communication import format_executive_response
from .orchestration import build_orchestration_plan

__all__ = [
    "ORKIO_IDENTITY",
    "build_reasoning_frame",
    "classify_truth_level",
    "TruthLevel",
    "CapabilityResolver",
    "classify_intent",
    "format_executive_response",
    "build_orchestration_plan",
]
