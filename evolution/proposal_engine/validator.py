from __future__ import annotations
from .proposal_models import Proposal

class ProposalValidator:
    def validate(self, proposal: Proposal) -> bool:
        proposal.validate_governance()
        if not proposal.title.strip():
            raise ValueError("proposal title is required")
        if not proposal.summary.strip():
            raise ValueError("proposal summary is required")
        if not proposal.recommendation.strip():
            raise ValueError("proposal recommendation is required")
        return True
