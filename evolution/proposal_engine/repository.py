from __future__ import annotations
from .proposal_models import Proposal

class ProposalRepository:
    def __init__(self) -> None:
        self._proposals: dict[str, Proposal] = {}

    def save(self, proposal: Proposal) -> dict:
        proposal.validate_governance()
        self._proposals[proposal.proposal_id] = proposal
        return proposal.to_dict()

    def list(self) -> list[dict]:
        return [proposal.to_dict() for proposal in self._proposals.values()]

    def get(self, proposal_id: str) -> dict | None:
        proposal = self._proposals.get(proposal_id)
        return proposal.to_dict() if proposal else None
