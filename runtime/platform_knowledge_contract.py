"""
ORKIO Platform Knowledge Contract
Pure-Python helper for future runtime integration.
No DB, no network, no side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional


CapabilityStatus = Literal[
    "production",
    "beta",
    "beta_admin",
    "planned",
    "proposal",
    "not_available_public_beta",
]


@dataclass(frozen=True)
class Capability:
    key: str
    status: CapabilityStatus
    public_label: str
    description: str
    evidence_level: str


CURRENT_CAPABILITIES: Dict[str, Capability] = {
    "chat": Capability("chat", "production", "Disponível", "Conversas com Orkio via interface web.", "runtime_observed"),
    "sse_streaming": Capability("sse_streaming", "production", "Disponível", "Streaming SSE em /api/chat/stream.", "runtime_observed"),
    "authentication": Capability("authentication", "production", "Disponível", "Login, sessão e heartbeat.", "runtime_observed"),
    "threads_messages": Capability("threads_messages", "production", "Disponível", "Threads e mensagens.", "runtime_observed"),
    "agents": Capability("agents", "beta", "Beta", "Agentes e roteamento interno em evolução.", "runtime_observed"),
    "executive_intelligence": Capability("executive_intelligence", "beta", "Beta", "EOS-06/AO85 para inteligência executiva.", "runtime_observed"),
    "governance_proposals": Capability("governance_proposals", "beta", "Beta", "Proposal_only, riscos, rollback e aprovação humana.", "schema_observed"),
    "autonomous_execution": Capability("autonomous_execution", "not_available_public_beta", "Não disponível", "Execução autônoma sem aprovação humana não está disponível.", "governance_rule"),
}


def get_capability(key: str) -> Optional[Capability]:
    return CURRENT_CAPABILITIES.get((key or "").strip().lower())


def list_capabilities(status: Optional[CapabilityStatus] = None) -> List[Capability]:
    values = list(CURRENT_CAPABILITIES.values())
    if status is None:
        return values
    return [cap for cap in values if cap.status == status]


def platform_answer_guard(question: str) -> Dict[str, object]:
    q = (question or "").lower()
    is_platform_question = any(term in q for term in [
        "o que é", "plataforma", "orkio", "consegue", "capacidade", "oferece", "roadmap", "produção", "beta"
    ])
    is_execution_question = any(term in q for term in [
        "deploy", "pull request", "pr", "merge", "executar", "criar código", "alterar backend"
    ])
    return {
        "is_platform_question": is_platform_question,
        "requires_truth_separation": is_platform_question,
        "must_state_human_approval": is_execution_question,
        "default_mode": "observe_only",
        "proposal_only": True,
    }
