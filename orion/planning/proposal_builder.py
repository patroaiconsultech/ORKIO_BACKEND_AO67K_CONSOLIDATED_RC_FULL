from __future__ import annotations

from orion.contracts.models import Diagnosis, EvolutionProposal
from orion.governance.risk_engine import RiskEngine


class ProposalBuilder:
    def __init__(self, risk_engine: RiskEngine | None = None) -> None:
        self.risk_engine = risk_engine or RiskEngine()

    def build(
        self,
        *,
        diagnosis: Diagnosis,
        objective: str,
        files: list[str],
        diff_preview: str,
        tests: list[str],
        rollback_strategy: str,
        branch_name: str,
    ) -> EvolutionProposal:
        risk = self.risk_engine.assess(files, diff_preview)
        return EvolutionProposal(
            objective=objective,
            files=files,
            diff_preview=diff_preview,
            tests=tests,
            rollback={"strategy": rollback_strategy, "commands": ["git revert <sha>"]},
            risk=risk,
            evidence_ids=list(diagnosis.evidence_ids),
            diagnosis_id=diagnosis.diagnosis_id,
            branch_name=branch_name,
        )
