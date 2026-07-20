from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = (ROOT / "alembic" / "versions" / "0038_patch_auth_password_reset_tokens.py").read_text(encoding="utf-8")
MODELS = (ROOT / "models.py").read_text(encoding="utf-8")
MAIN = (ROOT / "main.py").read_text(encoding="utf-8")


def test_runtime_model_and_migration_share_table_contract():
    assert 'class PasswordResetToken(Base):' in MODELS
    assert '__tablename__ = "password_reset_tokens"' in MODELS
    for column in ("id", "lead_id", "token_hash", "expires_at", "used_at", "created_at"):
        assert f'"{column}"' in MIGRATION


def test_runtime_persists_before_provider_dispatch():
    forgot_start = MAIN.index("def forgot_password")
    reset_start = MAIN.index('app.post("/api/auth/reset-password")', forgot_start)
    source = MAIN[forgot_start:reset_start]
    assert source.index("UPDATE password_reset_tokens") < source.index("db.commit()")
    assert source.index("db.commit()") < source.index("_send_password_reset_email(email, raw)")


def test_migration_never_bootstraps_from_request_runtime():
    assert "ALLOW_SCHEMA_BOOTSTRAP" not in MIGRATION
    assert "ensure_schema" not in MIGRATION
    assert "CREATE TABLE IF NOT EXISTS" not in MIGRATION


def test_existing_table_adoption_is_forbidden():
    assert "AUTH_RESET_001_TABLE_ALREADY_EXISTS" in MIGRATION
    assert "manual_baseline_review_required=true" in MIGRATION


def test_downgrade_is_contract_guarded():
    downgrade = MIGRATION[MIGRATION.index("def downgrade()"):]
    assert "_validate_contract(target_schema)" in downgrade
    assert "op.drop_table(_TABLE, schema=target_schema)" in downgrade


def test_schema_and_index_contract_are_explicit():
    assert "SELECT current_schema()" in MIGRATION
    assert "get_schema_names()" in MIGRATION
    assert "column_names" in MIGRATION
    assert 'bool(index.get("unique", False))' in MIGRATION
