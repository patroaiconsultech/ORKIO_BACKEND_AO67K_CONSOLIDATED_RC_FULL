import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = ROOT / "alembic" / "versions" / "0039_patch_evolution_intelligence_foundation.py"


def _assignments():
    tree = ast.parse(MIGRATION.read_text(encoding="utf-8"))
    values = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
            continue
        if node.targets[0].id in {"revision", "down_revision"}:
            values[node.targets[0].id] = ast.literal_eval(node.value)
    return values


def test_migration_extends_current_head():
    values = _assignments()
    assert values["revision"] == "0039_patch_evolution_intelligence_foundation"
    assert values["down_revision"] == "0038_patch_auth_password_reset_tokens"


def test_migration_is_proposal_only_and_tenant_scoped():
    source = MIGRATION.read_text(encoding="utf-8")
    assert '"org_slug"' in source
    assert "proposal_policy = 'proposal_only'" in source
    assert "auto_apply_enabled = FALSE" in source
    assert "human_approval_required = TRUE" in source
    assert "evolution_objectives" in source
    assert "evolution_kpi_targets" in source
    assert "evolution_health_snapshots" in source
    assert "scope_key" in source
    assert "fk_evolution_kpi_target_objective_org" in source
    assert "fk_evolution_health_objective_org" in source
    assert "ux_evolution_objective_org_name" in source
