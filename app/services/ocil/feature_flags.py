from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class OCILFeatureFlags:
    foundation_enabled: bool = True
    shadow_enabled: bool = True
    attachment_enforcement_enabled: bool = False
    execution_enforcement_enabled: bool = False
    agent_safety_enabled: bool = True
    network_egress_enabled: bool = False
    tool_execution_enabled: bool = False
    autonomous_actions_enabled: bool = False

    @classmethod
    def from_env(cls) -> "OCILFeatureFlags":
        return cls(
            foundation_enabled=_env_bool("OCIL_FOUNDATION_ENABLED", True),
            shadow_enabled=_env_bool("OCIL_SHADOW_ENABLED", True),
            attachment_enforcement_enabled=_env_bool(
                "OCIL_ATTACHMENT_ENFORCEMENT_ENABLED", False
            ),
            execution_enforcement_enabled=_env_bool(
                "OCIL_EXECUTION_ENFORCEMENT_ENABLED", False
            ),
            agent_safety_enabled=_env_bool("OCIL_AGENT_SAFETY_ENABLED", True),
            network_egress_enabled=_env_bool(
                "OCIL_NETWORK_EGRESS_ENABLED", False
            ),
            tool_execution_enabled=_env_bool(
                "OCIL_TOOL_EXECUTION_ENABLED", False
            ),
            autonomous_actions_enabled=_env_bool(
                "OCIL_AUTONOMOUS_ACTIONS_ENABLED", False
            ),
        )
