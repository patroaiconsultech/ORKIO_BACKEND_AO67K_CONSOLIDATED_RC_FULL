from __future__ import annotations

from typing import Any


class ProposalConflictDetector:
    """Minimal deterministic conflict detection for OEP-005.2."""

    def detect(self, proposals: list[dict[str, Any]]) -> list[dict[str, Any]]:
        conflicts: list[dict[str, Any]] = []
        seen_titles: dict[str, str] = {}

        for proposal in proposals:
            proposal_id = str(proposal.get("proposal_id") or proposal.get("id") or "")
            title = str(proposal.get("title") or "").strip().lower()
            if not title:
                continue
            if title in seen_titles:
                conflicts.append({
                    "type": "duplicate_title",
                    "proposal_id": proposal_id,
                    "conflicts_with": seen_titles[title],
                    "severity": "medium",
                    "proposal_only": True,
                    "requires_human_approval": True,
                })
            else:
                seen_titles[title] = proposal_id

        return conflicts
