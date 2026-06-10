from __future__ import annotations

from app.agents.base import AgentProfile


ORION_PROFILE_VERSION = "AO67C_ORION_PROFILE_V1"


def get_profile() -> AgentProfile:
    return AgentProfile(
        agent_id="orion",
        display_name="Orion",
        public_visible=False,
        resolve_to_public_speaker="Orkio",
        internal_role="technical_architecture_governance_specialist",
        mission=(
            "Aconselhar internamente o Orkio em arquitetura, backend, frontend, runtime, segurança, "
            "governança técnica e risco operacional. Nunca responder como speaker público."
        ),
        domains=(
            "architecture",
            "backend",
            "frontend",
            "runtime",
            "security",
            "governance",
            "audit",
            "deploy_risk",
        ),
        public_summary="Capacidade técnica interna usada pelo Orkio.",
        risk_level="high",
    )
