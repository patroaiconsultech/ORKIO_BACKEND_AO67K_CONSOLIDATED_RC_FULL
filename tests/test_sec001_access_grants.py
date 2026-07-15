from __future__ import annotations

import hashlib
import logging
import time
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.models import AuditLog, SignupCode
from app.routes.access_grants import AccessGrantRouterDeps, build_access_grants_router
from app.services.access_grant_service import (
    AccessGrantConfigurationError,
    AccessGrantInvalidError,
    decode_access_grant,
    find_signup_code_by_id,
    issue_access_grant,
    load_access_grant_config,
)


@pytest.fixture()
def env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ACCESS_GATE_SERVER_SIDE_ONLY", "true")
    monkeypatch.setenv("ACCESS_GATE_REQUIRE_FOR_AUTH", "true")
    monkeypatch.setenv("ACCESS_GATE_SIGNING_KEY", "k" * 64)
    monkeypatch.setenv("ACCESS_GATE_COOKIE_SECURE", "true")
    monkeypatch.setenv("ACCESS_GATE_COOKIE_SAMESITE", "lax")
    monkeypatch.setenv("ACCESS_GATE_BIND_USER_AGENT", "true")
    monkeypatch.setenv("ACCESS_GATE_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("ACCESS_CODE_MAX_ATTEMPTS", "2")
    monkeypatch.setenv("ACCESS_CODE_RATE_WINDOW_SECONDS", "300")
    monkeypatch.setenv("ACCESS_GRANT_TTL_SECONDS", "3600")
    monkeypatch.setenv("ACCESS_AUDIT_ENABLED", "true")


@pytest.fixture()
def app_client(env):
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(
        engine,
        tables=[SignupCode.__table__, AuditLog.__table__],
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    now = int(time.time())
    code = "SECURE-INVITE-EXAMPLE"
    with SessionLocal() as db:
        db.add(
            SignupCode(
                id="code-sec001",
                org_slug="public",
                code_hash=hashlib.sha256(code.upper().encode()).hexdigest(),
                label="investor",
                source="investor",
                expires_at=now + 3600,
                max_uses=3,
                used_count=0,
                active=True,
                created_at=now,
                created_by="test",
            )
        )
        db.commit()

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = FastAPI()
    app.include_router(
        build_access_grants_router(
            AccessGrantRouterDeps(
                get_db=get_db,
                get_org=lambda value: (value or "public").strip(),
                new_id=lambda: uuid.uuid4().hex,
                now_ts=lambda: int(time.time()),
                logger=logging.getLogger("sec001-test"),
            )
        )
    )
    return TestClient(app, base_url="https://testserver"), SessionLocal, code


def test_config_is_fail_closed_when_enabled_without_signing_key(monkeypatch):
    monkeypatch.setenv("ACCESS_GATE_SERVER_SIDE_ONLY", "true")
    monkeypatch.delenv("ACCESS_GATE_SIGNING_KEY", raising=False)
    with pytest.raises(AccessGrantConfigurationError):
        load_access_grant_config()


def test_signed_grant_detects_tamper_and_tenant(env, app_client):
    _, SessionLocal, _ = app_client
    with SessionLocal() as db:
        row = find_signup_code_by_id(
            db,
            org_slug="public",
            code_id="code-sec001",
            consume=False,
        )
        assert row is not None
        token, claims = issue_access_grant(
            code=row,
            org_slug="public",
            purpose="platform_beta",
            user_agent="ua-test",
            now=1000,
        )

    decoded = decode_access_grant(
        token,
        expected_org="public",
        user_agent="ua-test",
        now=1001,
    )
    assert decoded["code_id"] == "code-sec001"
    assert claims["exp"] > claims["iat"]

    with pytest.raises(AccessGrantInvalidError):
        decode_access_grant(
            token + "x",
            expected_org="public",
            user_agent="ua-test",
            now=1001,
        )

    with pytest.raises(AccessGrantInvalidError):
        decode_access_grant(
            token,
            expected_org="other",
            user_agent="ua-test",
            now=1001,
        )


def test_validate_status_and_revoke_cookie(app_client):
    client, _, code = app_client
    response = client.post(
        "/api/access-grants/validate",
        headers={"X-Org-Slug": "public", "User-Agent": "sec001-browser"},
        json={"code": code, "purpose": "platform_beta"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["granted"] is True
    assert "httponly" in response.headers["set-cookie"].lower()
    assert "secure" in response.headers["set-cookie"].lower()

    status = client.get(
        "/api/access-grants/status",
        headers={"X-Org-Slug": "public", "User-Agent": "sec001-browser"},
    )
    assert status.status_code == 200
    assert status.json()["granted"] is True

    revoked = client.post("/api/access-grants/revoke")
    assert revoked.status_code == 200
    assert revoked.json()["granted"] is False


def test_invalid_attempts_are_rate_limited(app_client):
    client, _, _ = app_client
    headers = {"X-Org-Slug": "public", "User-Agent": "sec001-rate"}
    for _ in range(2):
        response = client.post(
            "/api/access-grants/validate",
            headers=headers,
            json={"code": "WRONG-CODE", "purpose": "platform_beta"},
        )
        assert response.status_code == 401

    response = client.post(
        "/api/access-grants/validate",
        headers=headers,
        json={"code": "WRONG-CODE", "purpose": "platform_beta"},
    )
    assert response.status_code == 429


def test_repository_no_longer_embeds_retired_plaintext_codes():
    from pathlib import Path
    import re

    repo = Path(__file__).resolve().parents[1]
    targets = [
        repo / "main.py",
        repo / "routes" / "access_grants.py",
        repo / "services" / "access_grant_service.py",
        repo / "scripts" / "verify_realtime_contract.py",
    ]
    retired_hashes = {
        "4871d5c295f600e2bf4bfbc2bc850163ba4624337230479375f274387912e172",
        "4e58339d184b8f19068ec1828ac738a57a104500c878315a9adc0bbe6039f278",
        "24b6ab8d69e8c79401a7d9344fdbc519cd45a8c4e549c83bf058bb84901c5fef",
    }
    for path in targets:
        source = path.read_text(encoding="utf-8")
        tokens = re.findall(r"[A-Za-z0-9_-]{8,128}", source)
        assert not {
            hashlib.sha256(token.upper().encode("utf-8")).hexdigest()
            for token in tokens
        }.intersection(retired_hashes), path
