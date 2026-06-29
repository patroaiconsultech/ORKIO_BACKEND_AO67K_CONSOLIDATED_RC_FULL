from __future__ import annotations

from evolution.learning_engine.experience_repository import ExperienceRepository


class RecommendationEvolution:
    def __init__(self, repository: ExperienceRepository | None = None) -> None:
        self._repository = repository or ExperienceRepository()

    def summarize_pattern(self, query: str) -> dict:
        matches = self._repository.search(query)
        if not matches:
            success_rate = 0.0
            avg_score = 0.0
        else:
            scores = [float(item.get("score", 0.0)) for item in matches]
            avg_score = sum(scores) / len(scores)
            success_rate = len([score for score in scores if score >= 0.70]) / len(scores)

        return {
            "query": query,
            "matches": len(matches),
            "average_score": avg_score,
            "success_rate": success_rate,
            "recommendation": (
                "repeat_pattern" if success_rate >= 0.70 and matches else "insufficient_evidence"
            ),
            "proposal_only": True,
            "write_executed": False,
            "human_approval_required": True,
        }
