from __future__ import annotations

from pathlib import PurePosixPath
from typing import Iterable, List

from .premium_contracts import RiskAssessment


SENSITIVE_PARTS = {
    "auth": {"auth", "security", "token", "oauth", "jwt"},
    "database": {"alembic", "migration", "models.py", "db.py", "database"},
    "runtime_boot": {"main.py", "dockerfile", "railway", "startup", "release_identity"},
    "deploy": {"dockerfile", "railway", "deploy", "nixpacks", "procfile"},
}


class PremiumRiskEngine:
    """Deterministic risk scoring for Orion evolution proposals."""

    def assess(
        self,
        *,
        files: Iterable[str],
        diff_preview: str,
        declared_risk: str | None = None,
    ) -> RiskAssessment:
        normalized_files: List[str] = [str(PurePosixPath(str(item))).lower() for item in files]
        corpus = "\n".join(normalized_files + [str(diff_preview or "").lower()])

        touches_auth = any(token in corpus for token in SENSITIVE_PARTS["auth"])
        touches_database = any(token in corpus for token in SENSITIVE_PARTS["database"])
        touches_runtime_boot = any(token in corpus for token in SENSITIVE_PARTS["runtime_boot"])
        touches_deploy = any(token in corpus for token in SENSITIVE_PARTS["deploy"])

        score = 10
        reasons: List[str] = []

        file_count = len(normalized_files)
        if file_count == 0:
            score += 35
            reasons.append("proposal_without_files")
        elif file_count > 8:
            score += 25
            reasons.append("wide_file_blast_radius")
        elif file_count > 3:
            score += 12
            reasons.append("multi_file_change")

        changed_lines = sum(
            1 for line in str(diff_preview or "").splitlines()
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
        )
        if changed_lines == 0:
            score += 25
            reasons.append("missing_or_empty_diff_preview")
        elif changed_lines > 250:
            score += 25
            reasons.append("large_diff")
        elif changed_lines > 80:
            score += 12
            reasons.append("medium_diff")

        for flag, reason, increment in (
            (touches_auth, "touches_auth_or_security", 25),
            (touches_database, "touches_database_or_migrations", 25),
            (touches_runtime_boot, "touches_runtime_boot", 25),
            (touches_deploy, "touches_deploy", 20),
        ):
            if flag:
                score += increment
                reasons.append(reason)

        declared = str(declared_risk or "").strip().lower()
        if declared == "high":
            score = max(score, 70)
            reasons.append("declared_high_risk")
        elif declared == "medium":
            score = max(score, 40)

        score = max(0, min(100, score))
        level = "low" if score < 35 else "medium" if score < 70 else "high"
        blast_radius = "local" if file_count <= 2 else "module" if file_count <= 8 else "platform"

        return RiskAssessment(
            level=level,
            score=score,
            reasons=sorted(set(reasons)),
            blast_radius=blast_radius,
            touches_database=touches_database,
            touches_auth=touches_auth,
            touches_runtime_boot=touches_runtime_boot,
            touches_deploy=touches_deploy,
        )
