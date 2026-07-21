from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from starlette.requests import Request


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

main = importlib.import_module("app.main")


def _request():
    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/api/admin/system/version",
            "headers": [],
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "server": ("test", 80),
            "scheme": "http",
        }
    )


def test_admin_system_version_rejects_tenant_mismatch(monkeypatch):
    monkeypatch.setattr(main, "tenant_mode", lambda: "multi")
    with pytest.raises(HTTPException) as exc:
        main.admin_system_version(
            request=_request(),
            x_org_slug="tenant-b",
            _admin={"org": "tenant-a", "role": "admin", "sub": "admin-a"},
            db=object(),
        )
    assert exc.value.status_code == 403
    assert exc.value.detail == "Tenant mismatch"


def test_admin_system_version_passes_canonical_scope_to_identity(monkeypatch):
    monkeypatch.setattr(main, "tenant_mode", lambda: "multi")
    observed = {}

    def fake_build_release_identity(*args, **kwargs):
        observed.update(kwargs)
        return {
            "contract_version": "ORKIO-REL-ID-R1.1",
            "migration_in_sync": True,
        }

    monkeypatch.setattr(main, "build_release_identity", fake_build_release_identity)
    result = main.admin_system_version(
        request=_request(),
        x_org_slug="tenant-a",
        _admin={
            "org": "tenant-a",
            "role": "admin",
            "sub": "admin-a",
            "is_admin_master": False,
            "write_approval_authority": False,
        },
        db=object(),
    )

    assert result["ok"] is True
    assert observed["authenticated_org"] == "tenant-a"
    assert observed["authority_scope"] == "tenant_admin"
    assert observed["database"] is not None
