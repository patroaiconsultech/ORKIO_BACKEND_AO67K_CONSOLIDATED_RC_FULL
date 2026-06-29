from __future__ import annotations
from typing import Any
from .analyzer import ProposalAnalyzer
from .builder import ProposalBuilder
from .repository import ProposalRepository
from .validator import ProposalValidator

class ProposalService:
    def __init__(self, analyzer=None, builder=None, validator=None, repository=None) -> None:
        self._analyzer = analyzer or ProposalAnalyzer()
        self._builder = builder or ProposalBuilder()
        self._validator = validator or ProposalValidator()
        self._repository = repository or ProposalRepository()

    def create_proposal(self, knowledge_items: list[dict[str, Any]], objective: str) -> dict[str, Any]:
        analysis = self._analyzer.analyze(knowledge_items=knowledge_items, objective=objective)
        proposal = self._builder.build(analysis)
        self._validator.validate(proposal)
        return self._repository.save(proposal)

    def list_proposals(self) -> list[dict[str, Any]]:
        return self._repository.list()

    def get_proposal(self, proposal_id: str) -> dict[str, Any] | None:
        return self._repository.get(proposal_id)

def create_proposal_service() -> ProposalService:
    return ProposalService()
