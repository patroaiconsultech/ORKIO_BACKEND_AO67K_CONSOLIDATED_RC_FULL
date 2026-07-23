from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .premium_contracts import EvolutionPlan, SimulationReport


class PremiumSimulationEngine:
    """
    Side-effect-free validation of an evolution plan.

    It never writes source files, creates branches, commits or deploys.
    """

    def run(self, plan: EvolutionPlan, *, repo_root: str | Path | None = None) -> SimulationReport:
        root = Path(repo_root).resolve() if repo_root else None
        checks: List[Dict[str, object]] = []

        checks.append({
            "name": "proposal_only",
            "passed": bool(plan.proposal_only),
            "detail": plan.status,
        })
        checks.append({
            "name": "human_approval_required",
            "passed": bool(plan.requires_human_approval),
            "detail": "required" if plan.requires_human_approval else "missing",
        })
        checks.append({
            "name": "diff_preview_present",
            "passed": bool(str(plan.diff_preview or "").strip()),
            "detail": f"{len(str(plan.diff_preview or ''))} chars",
        })
        checks.append({
            "name": "rollback_present",
            "passed": bool(plan.rollback.strategy and plan.rollback.commands),
            "detail": plan.rollback.strategy,
        })
        checks.append({
            "name": "tests_present",
            "passed": bool(plan.tests),
            "detail": f"{len(plan.tests)} tests",
        })
        checks.append({
            "name": "no_write_executed",
            "passed": plan.write_executed is False,
            "detail": str(plan.write_executed),
        })

        if root:
            missing = []
            escaping = []
            for relative in plan.files:
                candidate = (root / relative).resolve()
                try:
                    candidate.relative_to(root)
                except ValueError:
                    escaping.append(relative)
                    continue
                if not candidate.exists():
                    missing.append(relative)

            checks.append({
                "name": "paths_inside_repo",
                "passed": not escaping,
                "detail": escaping,
            })
            checks.append({
                "name": "files_exist",
                "passed": not missing,
                "detail": missing,
            })

        passed = all(bool(check["passed"]) for check in checks)
        summary = "simulation_passed" if passed else "simulation_blocked"
        return SimulationReport(passed=passed, checks=checks, summary=summary)
