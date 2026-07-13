import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "diagnose_tenant_drift.py"
SPEC = importlib.util.spec_from_file_location("diagnose_tenant_drift", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_database_url_prefers_internal_railway_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://internal/db")
    monkeypatch.setenv("DATABASE_PUBLIC_URL", "postgresql://public/db")
    monkeypatch.setenv("DATABASE_URL_PUBLIC", "postgresql://public2/db")
    assert MODULE._database_url() == "postgresql://internal/db"


def test_database_url_falls_back_to_public_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_PUBLIC_URL", "postgresql://public/db")
    monkeypatch.setenv("DATABASE_URL_PUBLIC", "postgresql://public2/db")
    assert MODULE._database_url() == "postgresql://public/db"


def test_database_url_normalizes_postgres_scheme(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://internal/db")
    monkeypatch.delenv("DATABASE_PUBLIC_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL_PUBLIC", raising=False)
    assert MODULE._database_url() == "postgresql://internal/db"


def test_database_url_is_required(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_PUBLIC_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL_PUBLIC", raising=False)
    with pytest.raises(RuntimeError):
        MODULE._database_url()
