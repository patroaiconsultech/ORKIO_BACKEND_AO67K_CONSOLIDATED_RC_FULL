from pathlib import Path
import ast


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "main.py").read_text(encoding="utf-8-sig")
TREE = ast.parse(SOURCE)


def _function_source(name: str) -> str:
    node = next(
        item for item in ast.walk(TREE)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == name
    )
    lines = SOURCE.splitlines()
    return "\n".join(lines[node.lineno - 1:node.end_lineno])


def test_all_admin_evolution_routes_use_canonical_tenant_guard():
    route_functions = []
    for node in ast.walk(TREE):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        paths = []
        for decorator in node.decorator_list:
            if (
                isinstance(decorator, ast.Call)
                and isinstance(decorator.func, ast.Attribute)
                and isinstance(decorator.func.value, ast.Name)
                and decorator.func.value.id == "app"
                and decorator.args
                and isinstance(decorator.args[0], ast.Constant)
                and isinstance(decorator.args[0].value, str)
                and "/api/admin/evolution" in decorator.args[0].value
            ):
                paths.append(decorator.args[0].value)
        if paths:
            route_functions.append((node.name, paths, _function_source(node.name)))

    assert route_functions
    for name, paths, source in route_functions:
        assert "get_request_org(_admin, x_org_slug)" in source, (name, paths)
        assert "get_org(x_org_slug)" not in source, (name, paths)


def test_proposal_lookup_and_mutation_are_org_bound_and_db_only():
    getter = _function_source("_admin_evolution_get_proposal")
    updater = _function_source("_admin_evolution_update_status")
    dry_run = _function_source("_admin_evolution_create_dry_run_execution")

    assert "AND org_slug = :org_slug" in getter
    assert "_ADMIN_EVOLUTION_PROPOSALS" not in getter
    assert "evolution_db_unavailable" in getter

    assert updater.count("AND org_slug = :org_slug") >= 4
    assert "_ADMIN_EVOLUTION_PROPOSALS" not in updater
    assert "proposal_tenant_update_conflict" in updater

    assert "AND org_slug = :org_slug" in dry_run
    assert "proposal_tenant_update_conflict" in dry_run


def test_all_proposal_lookup_calls_supply_org_slug():
    for node in ast.walk(TREE):
        if not isinstance(node, ast.Call):
            continue
        if not (
            isinstance(node.func, ast.Name)
            and node.func.id == "_admin_evolution_get_proposal"
        ):
            continue
        assert any(keyword.arg == "org_slug" for keyword in node.keywords), (
            node.lineno,
            ast.unparse(node),
        )


def test_tenant_guard_canary_is_present():
    assert "EVOLUTION_ADMIN_TENANT_GUARD_BOOT_OK" in SOURCE
    assert "version=EA-TENANT-R1.1" in SOURCE
    assert "cross_tenant=fail_closed" in SOURCE


def test_status_mutation_uses_atomic_state_precondition():
    updater = _function_source("_admin_evolution_update_status")
    assert updater.count(
        "AND LOWER(status) IN ('pending_approval', 'draft')"
    ) == 2
    assert "proposal_tenant_update_conflict" in updater
