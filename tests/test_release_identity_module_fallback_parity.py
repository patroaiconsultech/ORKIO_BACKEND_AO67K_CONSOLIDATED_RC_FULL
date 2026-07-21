from __future__ import annotations

import ast
import hashlib
import os
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from sqlalchemy import text

from runtime.release_identity import build_release_identity as module_build_release_identity


ROOT = Path(__file__).resolve().parents[1]


def _load_main_fallback_builder():
    source = (ROOT / "main.py").read_text(encoding="utf-8-sig")
    tree = ast.parse(source)

    target_try = None
    for node in tree.body:
        if not isinstance(node, ast.Try):
            continue
        for statement in node.body:
            if not isinstance(statement, ast.ImportFrom):
                continue
            if statement.module == "app.runtime.release_identity":
                target_try = node
                break
        if target_try is not None:
            break

    assert target_try is not None
    assert target_try.handlers

    handler = target_try.handlers[0]
    module = ast.Module(body=handler.body, type_ignores=[])
    ast.fix_missing_locations(module)

    namespace: dict[str, Any] = {
        "__file__": str(ROOT / "main.py"),
        "os": os,
        "re": re,
        "ast": ast,
        "hashlib": hashlib,
        "Path": Path,
        "text": text,
        "_RELID_REQUIRED_CONTRACT_VERSION": "ORKIO-REL-ID-R1.1",
        "_release_identity_import_exc": ImportError(
            "release_identity_contract_incompatible"
        ),
    }
    exec(compile(module, str(ROOT / "main.py"), "exec"), namespace)
    return namespace["build_release_identity"]


def test_runtime_module_and_main_fallback_payload_parity() -> None:
    fallback_builder = _load_main_fallback_builder()
    app = SimpleNamespace(routes=[object(), object(), object()])
    environ = {
        "APP_ENV": "staging",
        "ORKIO_COMMIT_SHA": "abcdef1234567890",
        "ORKIO_GIT_BRANCH": "premium-r13",
        "ORKIO_DEPLOYMENT_ID": "deploy-123",
        "EVOLUTION_MARCO_ZERO_PREVIEW_ENABLED": "true",
        "EVOLUTION_MARCO_ZERO_WRITE_ENABLED": "false",
        "EVOLUTION_SIGNALS_SNAPSHOT_WRITE_ENABLED": "false",
        "EVOLUTION_AGENT_EVAL_WRITE_ENABLED": "false",
    }

    common = {
        "app_version": "2.4.0",
        "repo_root": ROOT,
        "runtime_main_path": ROOT / "main.py",
        "environ": environ,
        "database": None,
        "authenticated_org": "tenant-a",
        "authority_scope": "tenant_admin",
    }

    module_identity = module_build_release_identity(app, **common)
    fallback_identity = fallback_builder(app, **common)

    excluded = {
        "release_identity_source",
        "release_identity_import_error_type",
        "release_identity_fallback_reason",
    }
    comparable_module = {
        key: value for key, value in module_identity.items() if key not in excluded
    }
    comparable_fallback = {
        key: value for key, value in fallback_identity.items() if key not in excluded
    }

    assert comparable_fallback == comparable_module
    assert module_identity["release_identity_source"] == "runtime_module"
    assert fallback_identity["release_identity_source"] == "main_fallback"
    assert fallback_identity["release_identity_fallback_reason"] == "contract_incompatible"
