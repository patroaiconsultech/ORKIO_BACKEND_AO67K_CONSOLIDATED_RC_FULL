from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..contracts import AgentAuthorityContract, ExecutionProfileContract
from ..feature_flags import OCILFeatureFlags


@dataclass(frozen=True)
class CapabilityBoundaryDecision:
    allowed_capabilities: List[str]
    blocked_actions: List[str]
    execution_allowed: bool
    reason: str


def evaluate_capability_boundary(
    *,
    authority: AgentAuthorityContract,
    execution: ExecutionProfileContract,
    flags: OCILFeatureFlags,
) -> CapabilityBoundaryDecision:
    blocked_actions = [
        "write_repository",
        "commit",
        "deploy",
        "migration",
        "main_branch_write",
        "credential_access",
        "self_modification",
        "direct_agent_to_agent_call",
    ]

    if not flags.network_egress_enabled:
        blocked_actions.append("network_egress")

    if not flags.tool_execution_enabled:
        blocked_actions.append("tool_execution")

    requested = set(execution.required_capabilities)
    allowed = set(authority.allowed_capabilities)
    effective = sorted(requested.intersection(allowed))

    execution_allowed = (
        flags.agent_safety_enabled
        and flags.autonomous_actions_enabled
        and requested.issubset(allowed)
    )

    reason = (
        "explicit_capability_grant"
        if execution_allowed
        else "default_deny_or_missing_capability"
    )

    return CapabilityBoundaryDecision(
        allowed_capabilities=effective,
        blocked_actions=sorted(set(blocked_actions)),
        execution_allowed=execution_allowed,
        reason=reason,
    )
