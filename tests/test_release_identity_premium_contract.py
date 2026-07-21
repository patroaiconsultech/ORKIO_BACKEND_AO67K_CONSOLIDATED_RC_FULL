from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from runtime.release_identity import CONTRACT_VERSION, build_release_identity


ROOT = Path(__file__).resolve().parents[1]


def test_runtime_module_exposes_premium_source_metadata() -> None:
    identity = build_release_identity(
        FastAPI(),
        app_version="test",
        repo_root=ROOT,
        runtime_main_path=ROOT / "main.py",
        environ={},
    )

    assert CONTRACT_VERSION == "ORKIO-REL-ID-R1.1"
    assert identity["release_identity_source"] == "runtime_module"
    assert identity["release_identity_import_error_type"] == "none"
    assert identity["release_identity_fallback_reason"] == "not_applicable"


def test_main_validates_release_identity_contract_version() -> None:
    source = (ROOT / "main.py").read_text(encoding="utf-8-sig")

    assert '_RELID_REQUIRED_CONTRACT_VERSION = "ORKIO-REL-ID-R1.1"' in source
    assert "CONTRACT_VERSION as _RELID_MODULE_CONTRACT_VERSION" in source
    assert 'raise ImportError("release_identity_contract_incompatible")' in source
    assert '"release_identity_fallback_reason": _RELID_FALLBACK_REASON' in source


def test_startup_marks_identity_state_and_remains_fail_closed() -> None:
    source = (ROOT / "main.py").read_text(encoding="utf-8-sig")

    assert 'app.state.runtime_identity_validated = False' in source
    assert 'app.state.runtime_identity_status = "failed"' in source
    assert 'logger.exception("ORKIO_BOOT_IDENTITY_FAILED")' in source
    assert 'app.state.runtime_identity_status = "validated"' in source


def test_admin_system_version_exposes_boot_identity_gate() -> None:
    source = (ROOT / "main.py").read_text(encoding="utf-8-sig")

    assert '"runtime_identity_validated": bool(' in source
    assert '"runtime_identity_status": str(' in source
    assert '"boot_release_identity_source": str(' in source
    assert '"boot_runtime_main_sha256": str(' in source
    assert '"runtime_identity_consistent": bool(' in source
