import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = (
    ROOT
    / "alembic"
    / "versions"
    / "0040_patch_evolution_intelligence_premium_lineage.py"
)


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


def test_migration_extends_r15_head():
    values = _assignments()
    assert values["revision"] == "0040_patch_evolution_intelligence_premium_lineage"
    assert values["down_revision"] == "0039_patch_evolution_intelligence_foundation"


def test_migration_adds_versioning_provenance_and_immutable_events():
    source = MIGRATION.read_text(encoding="utf-8")
    assert "evolution_kpi_target_versions" in source
    assert "effective_from" in source
    assert "effective_to" in source
    assert "change_reason" in source
    assert "approval_id" in source
    assert "evolution_health_snapshot_provenance" in source
    assert "collector_version" in source
    assert "source_version" in source
    assert "content_sha256" in source
    assert "evolution_health_snapshot_events" in source
    assert "ORKIO_IMMUTABLE_RECORD" in source
    assert "BEFORE UPDATE OR DELETE" in source
    assert "ondelete=\"RESTRICT\"" in source
