"""
EO-03 — Capability Resolver.

Resolve capacidades a partir de um registry em memória.
RC-1 inclui fallback seguro; integração com YAML/JSON pode ser feita depois.
"""

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from .truth_engine import TruthLevel, classify_truth_level, label_for


@dataclass(frozen=True)
class Capability:
    id: str
    name: str
    status: str
    description: str
    limits: tuple[str, ...] = ()
    human_approval_required: bool = False


DEFAULT_CAPABILITIES: Dict[str, Capability] = {
    "chat": Capability(
        id="chat",
        name="Chat com Orkio",
        status="production",
        description="Conversas com o agente Orkio via interface web.",
    ),
    "sse_stream": Capability(
        id="sse_stream",
        name="Streaming SSE",
        status="production",
        description="Resposta em stream para o chat, com eventos de status e finalização.",
    ),
    "agents": Capability(
        id="agents",
        name="Agentes",
        status="production",
        description="Cadastro e seleção de agentes no ambiente da plataforma.",
    ),
    "files": Capability(
        id="files",
        name="Arquivos",
        status="beta",
        description="Upload e uso de documentos no contexto da plataforma, conforme configuração.",
    ),
    "governance": Capability(
        id="governance",
        name="Governança de evolução",
        status="beta",
        description="Fluxo de proposta, risco, validação, rollback e aprovação humana.",
        human_approval_required=True,
    ),
    "autonomous_deploy": Capability(
        id="autonomous_deploy",
        name="Deploy autônomo",
        status="proposal",
        description="Capacidade conceitual de execução automatizada; não disponível sem aprovação humana.",
        human_approval_required=True,
    ),
    "knowledge_canon": Capability(
        id="knowledge_canon",
        name="Canon institucional",
        status="roadmap",
        description="Base governada de conhecimento institucional e técnico.",
    ),
}


class CapabilityResolver:
    def __init__(self, capabilities: Optional[Dict[str, Capability]] = None) -> None:
        self.capabilities = capabilities or DEFAULT_CAPABILITIES

    def list_by_status(self, status: str) -> List[Capability]:
        return [c for c in self.capabilities.values() if c.status == status]

    def find(self, query: str) -> List[Capability]:
        text = (query or "").lower()
        result = []
        for cap in self.capabilities.values():
            hay = f"{cap.id} {cap.name} {cap.description}".lower()
            if any(token in hay for token in text.split() if len(token) > 2):
                result.append(cap)
        return result

    def explain(self, capabilities: Iterable[Capability]) -> str:
        lines = []
        for cap in capabilities:
            level = classify_truth_level(cap.status)
            lines.append(f"- {cap.name}: {label_for(level)} — {cap.description}")
            if cap.human_approval_required:
                lines.append("  - Requer aprovação humana para execução ou mudança estrutural.")
            for limit in cap.limits:
                lines.append(f"  - Limite: {limit}")
        return "\n".join(lines)

    def status_summary(self) -> str:
        order = ["production", "beta", "roadmap", "proposal"]
        labels = {
            "production": "Disponível agora",
            "beta": "Beta",
            "roadmap": "Roadmap",
            "proposal": "Proposta",
        }
        blocks = []
        for status in order:
            caps = self.list_by_status(status)
            if caps:
                blocks.append(labels[status] + ":")
                blocks.append(self.explain(caps))
        return "\n\n".join(blocks)
