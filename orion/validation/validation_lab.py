from __future__ import annotations

import compileall
import subprocess
import sys
from pathlib import Path

from orion.contracts.models import ExecutionReport, ValidationReport
from orion.execution.command_policy import CommandPolicy


class ValidationLab:
    def __init__(self, command_policy: CommandPolicy | None = None) -> None:
        self.command_policy = command_policy or CommandPolicy()

    def validate(
        self,
        execution: ExecutionReport,
        *,
        test_commands: list[list[str]] | None = None,
        timeout_seconds: int = 60,
    ) -> ValidationReport:
        root = Path(execution.workspace_path).resolve()
        checks: list[dict] = []
        blocking: list[str] = []

        checks.append({
            "name": "patch_applied",
            "passed": execution.applied,
            "detail": execution.stderr,
        })
        if not execution.applied:
            blocking.append("patch_application_failed")

        compile_ok = compileall.compile_dir(str(root), quiet=1)
        checks.append({"name": "compileall", "passed": compile_ok, "detail": ""})
        if not compile_ok:
            blocking.append("compile_failure")

        for command in test_commands or []:
            validated = self.command_policy.validate(command)
            proc = subprocess.run(
                validated,
                cwd=root,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            passed = proc.returncode == 0
            checks.append({
                "name": "test_command",
                "passed": passed,
                "detail": {"command": validated, "stdout": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]},
            })
            if not passed:
                blocking.append("test_failure")

        passed_count = sum(1 for check in checks if check["passed"])
        score = round((passed_count / max(1, len(checks))) * 100)
        status = "review_ready" if not blocking and score >= 80 else "blocked"
        return ValidationReport(
            patch_id=execution.patch_id,
            score=score,
            status=status,
            checks=checks,
            blocking_failures=sorted(set(blocking)),
        )
