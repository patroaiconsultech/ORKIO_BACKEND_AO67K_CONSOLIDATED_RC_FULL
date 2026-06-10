from __future__ import annotations

from typing import Any, Dict, Optional

from app.agents.base import AgentHook, build_internal_advice
from .knowledge import get_knowledge_cards
from .profile import get_profile


ORION_HOOKS_VERSION = "AO67C_ORION_HOOKS_V1"


def get_hooks() -> list[AgentHook]:
    return [
        AgentHook(
            hook_id="orion.internal.technical_architecture",
            agent_id="orion",
            family="specialist",
            label="arquitetura técnica interna",
            description="Aconselha o Orkio sobre arquitetura, runtime, backend, frontend e separação de camadas.",
            triggers=("arquitetura", "backend", "frontend", "runtime", "main.py", "appconsole", "hook", "mesh"),
            priority=80,
            public_safe=False,
            internal_only=True,
            synthesis_role="internal_technical_advice",
        ),
        AgentHook(
            hook_id="orion.internal.governance_guard",
            agent_id="orion",
            family="specialist",
            label="governança técnica interna",
            description="Aconselha o Orkio sobre segurança de superfície pública, rollback, deploy e risco de regressão.",
            triggers=("governança", "governanca", "autoevolução", "autoevolucao", "readonly", "patch", "deploy", "branch", "rollback"),
            priority=81,
            public_safe=False,
            internal_only=True,
            synthesis_role="internal_governance_advice",
        ),
    ]


def advise(message: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return build_internal_advice(
        agent_id="orion",
        message=message,
        profile=get_profile(),
        cards=get_knowledge_cards(),
        hooks=get_hooks(),
    )
