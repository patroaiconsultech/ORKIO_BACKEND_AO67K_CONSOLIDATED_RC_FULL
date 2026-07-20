from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "main.py").read_text(encoding="utf-8-sig")


def test_marco_zero_archive_endpoint_is_confirmed_and_soft_delete_free():
    assert '"/api/admin/evolution/archive-baseline"' in SOURCE
    assert '"/api/admin/evolution/proposals/archive-baseline"' in SOURCE
    assert "EFATA777_MARCO_ZERO" in SOURCE
    assert "marco_zero_confirmation_required" in SOURCE
    assert "delete_executed" in SOURCE
    assert "status = 'archived'" in SOURCE
    assert "EVOLUTION_MARCO_ZERO_ROUTE_ALIAS_BOOT_OK" in SOURCE


def test_marco_zero_route_precedes_dynamic_proposal_detail_route():
    archive_index = SOURCE.index('"/api/admin/evolution/archive-baseline"')
    legacy_archive_index = SOURCE.index('"/api/admin/evolution/proposals/archive-baseline"')
    detail_index = SOURCE.index('"/api/admin/evolution/proposals/{proposal_id}"')
    assert archive_index < detail_index
    assert legacy_archive_index < detail_index


def test_default_proposal_list_hides_archived_rows_but_keeps_audit_access():
    assert "include_archived: bool = False" in SOURCE
    assert "LOWER(status) <> 'archived'" in SOURCE
    assert "status=archived/include_archived=true" in SOURCE
