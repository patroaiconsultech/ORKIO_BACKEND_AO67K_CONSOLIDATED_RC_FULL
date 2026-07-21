from __future__ import annotations

import hashlib
import logging
import time
import uuid

from fastapi import HTTPException
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.requests import Request

from app.db import Base
from app.models import AuditLog, SignupCode
from app.routes.access_grants import AccessGrantRouterDeps, build_access_grants_router
from app.services.access_grant_service import require_request_access_grant


def _build(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ACCESS_GATE_SERVER_SIDE_ONLY", "true")
    monkeypatch.setenv("ACCESS_GATE_SIGNING_KEY", "k" * 64)
    monkeypatch.setenv("ACCESS_GATE_COOKIE_SECURE", "true")
    monkeypatch.setenv("ACCESS_GATE_COOKIE_SAMESITE", "lax")
    monkeypatch.setenv("ACCESS_GATE_BIND_USER_AGENT", "true")
    monkeypatch.setenv("ACCESS_GATE_HEADER_TRANSPORT_ENABLED", "true")
    monkeypatch.setenv("ACCESS_CODE_MAX_ATTEMPTS", "5")
    monkeypatch.setenv("ACCESS_CODE_RATE_WINDOW_SECONDS", "300")
    monkeypatch.setenv("ACCESS_GRANT_TTL_SECONDS", "3600")

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
    plain_code = "HEADER-BRIDGE-TEST"
    with SessionLocal() as db:
        db.add(
            SignupCode(
                id="code-r17",
                org_slug="public",
                code_hash=hashlib.sha256(plain_code.upper().encode()).hexdigest(),
                label="partner",
                source="test",
                expires_at=now + 3600,
                max_uses=5,
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
                logger=logging.getLogger("r17-header-bridge"),
            )
        )
    )
    return TestClient(app, base_url="https://testserver"), SessionLocal, plain_code


def _request_with_header(token: str, user_agent: str = "r17-browser") -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/api/auth/register",
            "headers": [
                (b"user-agent", user_agent.encode("ascii")),
                (b"x-orkio-access-grant", token.encode("ascii")),
            ],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 443),
            "scheme": "https",
            "query_string": b"",
        }
    )


def test_validate_returns_signed_header_grant(monkeypatch):
    client, _, code = _build(monkeypatch)
    response = client.post(
        "/api/access-grants/validate",
        headers={"X-Org-Slug": "public", "User-Agent": "r17-browser"},
        json={"code": code, "purpose": "platform_beta"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["granted"] is True
    assert isinstance(payload["grant_token"], str)
    assert "." in payload["grant_token"]


def test_header_grant_is_accepted_without_cookie(monkeypatch):
    client, SessionLocal, code = _build(monkeypatch)
    validated = client.post(
        "/api/access-grants/validate",
        headers={"X-Org-Slug": "public", "User-Agent": "r17-browser"},
        json={"code": code, "purpose": "platform_beta"},
    )
    token = validated.json()["grant_token"]

    with SessionLocal() as db:
        claims = require_request_access_grant(
            _request_with_header(token),
            expected_org="public",
            db=db,
        )

    assert claims["code_id"] == "code-r17"
    assert claims["_transport"] == "header"


def test_header_transport_disabled_fails_closed(monkeypatch):
    client, SessionLocal, code = _build(monkeypatch)
    validated = client.post(
        "/api/access-grants/validate",
        headers={"X-Org-Slug": "public", "User-Agent": "r17-browser"},
        json={"code": code, "purpose": "platform_beta"},
    )
    token = validated.json()["grant_token"]
    monkeypatch.setenv("ACCESS_GATE_HEADER_TRANSPORT_ENABLED", "false")

    with SessionLocal() as db:
        try:
            require_request_access_grant(
                _request_with_header(token),
                expected_org="public",
                db=db,
            )
        except HTTPException as exc:
            assert exc.status_code == 403
            assert exc.detail == "ACCESS_GRANT_REQUIRED"
        else:
            raise AssertionError("Disabled header transport must fail closed.")
