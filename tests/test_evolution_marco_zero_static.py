from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "main.py").read_text(encoding="utf-8-sig")


def test_marco_zero_routes_are_preview_only_and_registered_before_dynamic_detail():
    canonical = '"/api/admin/evolution/archive-baseline"'
    legacy = '"/api/admin/evolution/proposals/archive-baseline"'
    detail = '"/api/admin/evolution/proposals/{proposal_id}"'

    assert canonical in SOURCE
    assert legacy in SOURCE
    assert SOURCE.index(canonical) < SOURCE.index(detail)
    assert SOURCE.index(legacy) < SOURCE.index(detail)

    assert "EVOLUTION_MARCO_ZERO_ROUTE_ALIAS_BOOT_OK" in SOURCE
    assert "version=MZ-001-R1" in SOURCE
    assert "mode=preview_only" in SOURCE
    assert "write_enabled=false" in SOURCE


def test_marco_zero_is_tenant_bound_db_only_and_fail_closed():
    assert "org = get_request_org(_admin, x_org_slug)" in SOURCE
    assert "EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED" in SOURCE
    assert "EVOLUTION_MARCO_ZERO_PREVIEW_DISABLED" in SOURCE
    assert "EVOLUTION_MARCO_ZERO_WRITE_DISABLED" in SOURCE
    assert '"memory_fallback_used": False' in SOURCE
    assert '"schema_bootstrap_executed": False' in SOURCE
    assert '"database_write_executed": False' in SOURCE
    assert "COUNT(*) AS candidate_count" in SOURCE
    assert "LIMIT 50" in SOURCE


def test_marco_zero_does_not_embed_client_confirmation_or_write_sql():
    start = SOURCE.index("def _admin_evolution_archive_baseline")
    end = SOURCE.index("def _admin_evolution_list_executions", start)
    helper_source = SOURCE[start:end]

    assert "EFATA777_MARCO_ZERO" not in SOURCE
    assert "UPDATE admin_evolution_proposals" not in helper_source
    assert "DELETE FROM admin_evolution_proposals" not in helper_source
    assert "_ADMIN_EVOLUTION_PROPOSALS" not in helper_source
    assert "_admin_evolution_bootstrap_db_schema()" not in helper_source


def test_default_proposal_list_still_hides_archived_rows_and_preserves_audit_access():
    assert "include_archived: bool = False" in SOURCE
    assert "LOWER(status) <> 'archived'" in SOURCE
