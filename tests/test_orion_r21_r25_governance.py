from pathlib import Path

import pytest

from orion.contracts.models import EvolutionProposal, PatchArtifact
from orion.execution.command_policy import CommandPolicy, CommandPolicyError
from orion.execution.path_allowlist import PathAllowlist, PathPolicyError
from orion.governance.execution_guard import ExecutionGuard
from orion.governance.permission_matrix import PermissionMatrix


def proposal() -> EvolutionProposal:
    item = EvolutionProposal(
        objective="safe patch",
        files=["orion/example.py"],
        diff_preview="--- a/orion/example.py\n+++ b/orion/example.py\n@@\n-old\n+new\n",
        tests=["python -m pytest"],
        rollback={"strategy": "git_revert", "commands": ["git revert <sha>"]},
        risk={"level": "low", "score": 10},
        branch_name="orion/r25-test",
    )
    return item


def patch(item: EvolutionProposal) -> PatchArtifact:
    return PatchArtifact(
        proposal_id=item.proposal_id,
        unified_diff=item.diff_preview,
        files_changed=item.files,
        before_hashes={},
        expected_after_hashes={},
    )


def test_global_production_and_push_permissions_are_forbidden():
    matrix = PermissionMatrix()
    assert matrix.allows("kernel", "deploy_production") is False
    assert matrix.allows("execution", "push_remote") is False
    assert matrix.allows("execution", "write_primary_repository") is False


def test_guard_requires_named_human_approval():
    item = proposal()
    decision = ExecutionGuard().evaluate_branch_execution(item, patch(item))
    assert decision.allowed is False
    assert "human_approval_missing" in decision.reasons


def test_guard_blocks_production_even_after_approval():
    item = proposal()
    item.approve("human-reviewer")
    decision = ExecutionGuard().evaluate_branch_execution(
        item, patch(item), target_environment="production"
    )
    assert decision.allowed is False
    assert "production_execution_forbidden" in decision.reasons


def test_safe_branch_execution_can_pass_governance():
    item = proposal()
    item.approve("human-reviewer")
    decision = ExecutionGuard().evaluate_branch_execution(item, patch(item))
    assert decision.allowed is True


@pytest.mark.parametrize("path", ["../secret", ".env", ".git/config", "auth/login.py", "Dockerfile"])
def test_sensitive_paths_are_blocked(path):
    with pytest.raises(PathPolicyError):
        PathAllowlist().validate([path])


def test_arbitrary_shell_is_blocked():
    with pytest.raises(CommandPolicyError):
        CommandPolicy().validate(["bash", "-c", "echo unsafe"])
