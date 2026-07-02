from typing import Dict, Any

DEFAULT_GOVERNANCE_FLAGS = {
    "mode": "observe_only",
    "proposal_only": True,
    "write_executed": False,
    "branch_created": False,
    "pr_created": False,
    "deploy_executed": False,
    "human_approval_required": True,
}

def governance_flags(overrides: Dict[str, Any] | None = None) -> Dict[str, Any]:
    flags = dict(DEFAULT_GOVERNANCE_FLAGS)
    if overrides:
        flags.update(overrides)
    return flags
