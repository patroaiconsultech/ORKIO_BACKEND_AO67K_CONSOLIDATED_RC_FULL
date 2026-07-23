from __future__ import annotations

from typing import Iterable, Dict, Any


class RiskEngine:
    SENSITIVE = {
        "auth": ("auth/", "security/", "jwt", "oauth"),
        "database": ("alembic/", "migrations/", "models.py", "database"),
        "deploy": ("dockerfile", "railway", "procfile", "deploy"),
        "runtime": ("main.py", "startup", "release_identity"),
    }

    def assess(self, files: Iterable[str], diff_preview: str) -> Dict[str, Any]:
        normalized = [str(item).replace("\\", "/").lower() for item in files]
        corpus = "\n".join(normalized + [str(diff_preview or "").lower()])
        score = 10
        reasons: list[str] = []

        if not normalized:
            score += 35
            reasons.append("proposal_without_files")
        if len(normalized) > 8:
            score += 25
            reasons.append("platform_blast_radius")
        elif len(normalized) > 3:
            score += 12
            reasons.append("multi_file_change")

        changed_lines = sum(
            1 for line in str(diff_preview or "").splitlines()
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
        )
        if changed_lines == 0:
            score += 25
            reasons.append("empty_diff")
        elif changed_lines > 250:
            score += 25
            reasons.append("large_diff")
        elif changed_lines > 80:
            score += 12
            reasons.append("medium_diff")

        touched: dict[str, bool] = {}
        for category, tokens in self.SENSITIVE.items():
            flag = any(token in corpus for token in tokens)
            touched[category] = flag
            if flag:
                score += 25 if category in {"auth", "database", "runtime"} else 20
                reasons.append(f"touches_{category}")

        score = min(score, 100)
        level = "low" if score < 35 else "medium" if score < 70 else "high"
        return {
            "score": score,
            "level": level,
            "reasons": sorted(set(reasons)),
            "touches": touched,
        }
