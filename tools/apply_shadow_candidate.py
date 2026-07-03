#!/usr/bin/env python3
"""
ORKIO CORE RC2-R2 Runtime Foundation — Repo-Ready Shadow Applier R1.

This script is intentionally repo-ready:
- It expects to run from the backend repository root after the ZIP contents
  were copied/extracted into that root.
- It does NOT look for payload/.
- It refuses to run unless HEAD is the locked baseline SHA.
- It refuses pre-existing app/config/runtime.py before planning/writing.
- It applies only approved target-only import hygiene replacements.
- It does not edit main.py, SSE routes, database migrations, routers, guards,
  or production behavior.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

EXPECTED_BASELINE_SHA = "94ba9246bcd3d2a5c40d42657ae7ca17c80a2826"

# Files expected to be present after repo-ready extraction/upload.
# They are not copied from payload/; repo-ready means they already live at
# their final repository paths.
REPO_READY_FILES = (
    "runtime/orkio_runtime_foundation/persistence.py",
    "tests/runtime/test_runtime_persistence_shadow.py",
    "architecture/contracts/runtime_persistence_canonical_contract.md",
    "engineering/EPIC002B_CANONICAL_ASSISTANT_MESSAGE_ID_SHADOW_LOCKED.md",
    "engineering/VALIDACAO_LOCAL_EPIC002B.md",
    "adrs/ADR-0003-runtime-persistence-canonical-assistant-message-id.md",
)

REPLACEMENTS = {
    Path("runtime/intent_engine.py"): (
        ("from app.config.runtime import RUNTIME_FLAGS", "from config.runtime import RUNTIME_FLAGS"),
        ("from app.services.governance_service import evaluate_governance_action", "from services.governance_service import evaluate_governance_action"),
        ("from app.runtime.capability_registry import", "from runtime.capability_registry import"),
    ),
    Path("services/governance_service.py"): (
        ("from app.core.orkio_constitution import", "from core.orkio_constitution import"),
        ("import app.core.orkio_constitution", "import core.orkio_constitution"),
        ("from app.core.orkio_identity import", "from core.orkio_identity import"),
        ("from app.core.orkio_permissions import", "from core.orkio_permissions import"),
        ("from app.core", "from core"),
        ("import app.core", "import core"),
        ("from app.services.capability_service import", "from services.capability_service import"),
        ("import app.services.capability_service", "import services.capability_service"),
    ),
    Path("services/capability_service.py"): (
        ("app.core.orkio_capabilities", "core.orkio_capabilities"),
    ),
}

REQUIRED_BASELINE_FILES = (
    "config/runtime.py",
    "runtime/intent_engine.py",
    "runtime/capability_registry.py",
    "services/governance_service.py",
    "services/capability_service.py",
    "core/orkio_constitution.py",
    "core/orkio_identity.py",
    "core/orkio_permissions.py",
    "core/orkio_capabilities.py",
)

FORBIDDEN_PREEXISTING_PATHS = (
    "app/config/runtime.py",
)


class ApplyError(RuntimeError):
    pass


def run_git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise ApplyError("not a git repository or git HEAD unavailable: " + result.stderr.strip())
    return result.stdout.strip()


def ensure_expected_git_sha(root: Path) -> None:
    actual = run_git_head(root)
    if actual != EXPECTED_BASELINE_SHA:
        raise ApplyError(
            f"baseline SHA mismatch: expected {EXPECTED_BASELINE_SHA}, got {actual}"
        )


def ensure_no_forbidden_preexisting_paths(root: Path) -> None:
    for rel in FORBIDDEN_PREEXISTING_PATHS:
        if (root / rel).exists():
            raise ApplyError(
                f"forbidden pre-existing shim/path detected before write: {rel}"
            )


def ensure_environment(root: Path) -> None:
    for rel in REQUIRED_BASELINE_FILES:
        if not (root / rel).exists():
            raise ApplyError(f"required baseline file missing: {rel}")
    for rel in REPO_READY_FILES:
        if not (root / rel).exists():
            raise ApplyError(f"repo-ready file missing after extraction/upload: {rel}")


def transform_text(text: str, replacements: tuple[tuple[str, str], ...]) -> tuple[str, list[str]]:
    changed: list[str] = []
    out = text
    for old, new in replacements:
        if old in out:
            out = out.replace(old, new)
            changed.append(f"{old} -> {new}")
    return out, changed


def apply_changes(root: Path, write: bool) -> list[str]:
    summary: list[str] = []

    # Verify repo-ready files are present. No payload copy in repo-ready mode.
    for rel in REPO_READY_FILES:
        path = root / rel
        if not path.exists():
            raise ApplyError(f"repo-ready file missing: {rel}")

    # Import hygiene.
    for target, replacements in REPLACEMENTS.items():
        path = root / target
        if not path.exists():
            raise ApplyError(f"target file missing: {target}")
        original = path.read_text(encoding="utf-8")
        new_text, changed = transform_text(original, replacements)
        if changed:
            summary.append(f"IMPORT {target}: " + "; ".join(changed))
            if write:
                path.write_text(new_text, encoding="utf-8")

    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".", help="Repository root. Default: current directory.")
    parser.add_argument("--check", action="store_true", help="Validate without writing.")
    parser.add_argument("--write", action="store_true", help="Apply changes.")
    args = parser.parse_args()

    if args.check == args.write:
        print("Choose exactly one: --check or --write", file=sys.stderr)
        return 2

    root = Path(args.repo).resolve()

    try:
        ensure_expected_git_sha(root)
        ensure_no_forbidden_preexisting_paths(root)
        ensure_environment(root)
        summary = apply_changes(root, write=args.write)
    except ApplyError as exc:
        print(f"RC2_REPO_READY_APPLIER_FAIL: {exc}", file=sys.stderr)
        return 1

    mode = "WRITE" if args.write else "CHECK"
    if summary:
        print(f"RC2_REPO_READY_APPLIER_{mode}: PASS")
        for item in summary:
            print(f"- {item}")
    else:
        print(f"RC2_REPO_READY_APPLIER_{mode}: PASS_NOOP_ALREADY_APPLIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
