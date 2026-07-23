from __future__ import annotations

import subprocess
from pathlib import Path

from orion.contracts.models import ExecutionReport, GovernanceDecision, PatchArtifact
from .command_policy import CommandPolicy
from .path_allowlist import PathAllowlist


class PatchExecutor:
    def __init__(
        self,
        path_policy: PathAllowlist | None = None,
        command_policy: CommandPolicy | None = None,
    ) -> None:
        self.path_policy = path_policy or PathAllowlist()
        self.command_policy = command_policy or CommandPolicy()

    def apply(
        self,
        patch: PatchArtifact,
        authorization: GovernanceDecision,
        workspace: str | Path,
        *,
        timeout_seconds: int = 30,
    ) -> ExecutionReport:
        if not authorization.allowed:
            raise PermissionError("governance_decision_denied")

        root = Path(workspace).resolve()
        self.path_policy.validate(patch.files_changed)

        proc = subprocess.run(
            ["patch", "-p1", "--forward", "--batch"],
            cwd=root,
            input=patch.unified_diff,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        return ExecutionReport(
            patch_id=patch.patch_id,
            workspace_path=str(root),
            applied=proc.returncode == 0,
            files_changed=list(patch.files_changed),
            stdout=proc.stdout,
            stderr=proc.stderr,
            commands_executed=[["patch", "-p1", "--forward", "--batch"]],
        )

    def run_allowed_test(
        self,
        command: list[str],
        workspace: str | Path,
        *,
        timeout_seconds: int = 60,
    ) -> subprocess.CompletedProcess[str]:
        validated = self.command_policy.validate(command)
        return subprocess.run(
            validated,
            cwd=Path(workspace).resolve(),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
