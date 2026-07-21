from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = (ROOT / "main.py").read_text(encoding="utf-8").lstrip("\ufeff")
SERVICE = (ROOT / "services/access_grant_service.py").read_text(encoding="utf-8").lstrip("\ufeff")


def test_main_parses() -> None:
    ast.parse(MAIN)


def test_access_grant_service_parses() -> None:
    ast.parse(SERVICE)


def test_login_and_register_use_route_specific_gates() -> None:
    assert "if access_gate_login_required():" in MAIN
    assert "if access_gate_register_required():" in MAIN


def test_reset_is_atomic_and_revokes_all_tokens() -> None:
    assert ".with_for_update()" in MAIN
    assert "all_tokens_revoked=true" in MAIN
    assert "WHERE lead_id = :uid AND used_at IS NULL" in MAIN


def test_failed_delivery_invalidates_new_token() -> None:
    assert "FORGOT_PASSWORD_PROVIDER_REJECTED" in MAIN
    assert "WHERE id = :token_id AND used_at IS NULL" in MAIN


def test_no_raw_reset_token_is_logged() -> None:
    forbidden = [
        "logger.info(raw",
        "logger.warning(raw",
        "logger.error(raw",
        "logger.exception(raw",
    ]
    assert not any(item in MAIN for item in forbidden)
