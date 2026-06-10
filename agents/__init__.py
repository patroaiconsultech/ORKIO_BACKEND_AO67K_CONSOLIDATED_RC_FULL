from __future__ import annotations

"""
AO67C — Agent Knowledge Modules

Camada de conhecimento individual dos agentes.

Contrato público:
- Orkio é o único speaker público.
- Especialistas internos podem aconselhar a malha.
- Nenhum módulo aqui deve chamar LLM, banco, rede, deploy, Git ou filesystem.
"""

from .registry import (
    AGENT_KNOWLEDGE_REGISTRY_VERSION,
    PUBLIC_VISIBLE_AGENT_NAME,
    build_agent_knowledge_snapshot,
    get_agent_profile,
    list_agent_profiles,
    collect_agent_hooks,
    collect_agent_advice,
)

__all__ = [
    "AGENT_KNOWLEDGE_REGISTRY_VERSION",
    "PUBLIC_VISIBLE_AGENT_NAME",
    "build_agent_knowledge_snapshot",
    "get_agent_profile",
    "list_agent_profiles",
    "collect_agent_hooks",
    "collect_agent_advice",
]
