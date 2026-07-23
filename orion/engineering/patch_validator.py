from __future__ import annotations

from orion.contracts.models import EvolutionProposal, PatchArtifact
from orion.execution.path_allowlist import PathAllowlist


class PatchValidator:
    def __init__(self, path_policy: PathAllowlist | None = None) -> None:
        self.path_policy = path_policy or PathAllowlist()

    def validate(self, proposal: EvolutionProposal, patch: PatchArtifact) -> list[str]:
        errors: list[str] = []
        try:
            self.path_policy.validate(patch.files_changed)
        except ValueError as exc:
            errors.append(str(exc))
        if patch.proposal_id != proposal.proposal_id:
            errors.append("patch_proposal_mismatch")
        if set(patch.files_changed) != set(proposal.files):
            errors.append("patch_scope_mismatch")
        if not patch.unified_diff.strip():
            errors.append("empty_patch")
        if patch.unified_diff != proposal.diff_preview:
            errors.append("approved_diff_mismatch")
        return sorted(set(errors))
