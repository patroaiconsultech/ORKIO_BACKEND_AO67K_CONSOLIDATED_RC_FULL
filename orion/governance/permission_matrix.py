from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet


@dataclass(frozen=True)
class PermissionMatrix:
    permissions: Dict[str, FrozenSet[str]] = field(default_factory=lambda: {
        "kernel": frozenset({"read", "orchestrate"}),
        "perception": frozenset({"read"}),
        "reasoning": frozenset({"read", "diagnose"}),
        "planning": frozenset({"read", "propose"}),
        "engineering": frozenset({"read", "generate_diff"}),
        "execution": frozenset({"read", "write_sandbox", "run_allowed_commands"}),
        "validation": frozenset({"read", "run_allowed_commands"}),
        "governance": frozenset({"read", "allow", "block"}),
        "learning": frozenset({"read", "record_outcome"}),
    })

    globally_forbidden: FrozenSet[str] = frozenset({
        "deploy_production",
        "push_remote",
        "approve_as_human",
        "edit_policy_runtime",
        "read_secrets",
        "write_primary_repository",
    })

    def allows(self, role: str, action: str) -> bool:
        if action in self.globally_forbidden:
            return False
        return action in self.permissions.get(role, frozenset())
