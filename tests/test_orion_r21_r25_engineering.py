from pathlib import Path

from orion.contracts.models import Diagnosis
from orion.engineering.diff_generator import DiffGenerator
from orion.engineering.patch_validator import PatchValidator
from orion.planning.proposal_builder import ProposalBuilder


def test_diff_generation_and_validation(tmp_path):
    target = tmp_path / "sample.py"
    target.write_text("VALUE = 1\n", encoding="utf-8")
    diagnosis = Diagnosis(
        primary_root_cause="test",
        evidence_ids=["e1"],
        confidence=1.0,
        affected_files=["sample.py"],
    )
    draft_diff = DiffGenerator().generate_for_file(
        repo_root=tmp_path,
        relative_path="sample.py",
        new_content="VALUE = 2\n",
        proposal_id="temporary",
    ).unified_diff
    proposal = ProposalBuilder().build(
        diagnosis=diagnosis,
        objective="change value",
        files=["sample.py"],
        diff_preview=draft_diff,
        tests=["python -m pytest"],
        rollback_strategy="git_revert",
        branch_name="orion/change-value",
    )
    patch = DiffGenerator().generate_for_file(
        repo_root=tmp_path,
        relative_path="sample.py",
        new_content="VALUE = 2\n",
        proposal_id=proposal.proposal_id,
    )
    assert PatchValidator().validate(proposal, patch) == []
