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


def test_release_identity_endpoint_is_admin_and_tenant_scoped():
    source = _function_source("admin_system_version")
    assert 'Depends(require_admin_access)' in source
    assert 'Depends(get_db)' in source
    assert 'get_request_org(_admin, x_org_slug)' in source
    assert 'authenticated_org=org' in source
    assert 'authority_scope=authority_scope' in source
    assert 'database=db' in source
    assert 'ADMIN_SYSTEM_VERSION_ACCESSED' in source
    assert 'audit(' not in source
    assert '@app.get("/api/admin/system/version")' in SOURCE
    assert '@app.get("/api/system/version")' not in SOURCE


def test_boot_identity_correlates_database_revision():
    source = _function_source("_startup_release_identity_r11")
    assert 'emit_boot_identity(' in source
    assert 'app_version=APP_VERSION' in source
    assert 'runtime_main_path=Path(__file__).resolve()' in source
    assert 'database=ENGINE' in source


def test_phase_a_contains_tenant_and_release_canaries():
    assert "EVOLUTION_ADMIN_TENANT_GUARD_BOOT_OK" in SOURCE
    assert "version=EA-TENANT-R1.1" in SOURCE
    release_source = (ROOT / "runtime" / "release_identity.py").read_text()
    assert "ORKIO_BOOT_IDENTITY" in release_source
    assert 'CONTRACT_VERSION = "ORKIO-REL-ID-R1.1"' in release_source
    assert "migration_database_revisions" in release_source
    assert "migration_in_sync" in release_source
