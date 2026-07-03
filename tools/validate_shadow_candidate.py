#!/usr/bin/env python3
"""
ORKIO CORE RC2 Runtime Foundation — Shadow Candidate Validator.

Targeted validation only. It verifies that the approved import edges have
been normalized and no forbidden shim from this package is present.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

EXPECTED = {
    "runtime/intent_engine.py": [
        "from config.runtime import RUNTIME_FLAGS",
        "from services.governance_service import evaluate_governance_action",
        "from runtime.capability_registry import",
    ],
    "services/governance_service.py": [
        "from core.orkio_constitution import",
        "from core.orkio_identity import",
        "from core.orkio_permissions import",
        "from services.capability_service import",
    ],
    "services/capability_service.py": [
        "core.orkio_capabilities",
    ],
}

FORBIDDEN = {
    "runtime/intent_engine.py": [
        "from app.config.runtime import RUNTIME_FLAGS",
        "from app.services.governance_service import evaluate_governance_action",
        "from app.runtime.capability_registry import",
    ],
    "services/governance_service.py": [
        "from app.core",
        "import app.core",
        "from app.services.capability_service import",
        "import app.services.capability_service",
    ],
    "services/capability_service.py": [
        "app.core.orkio_capabilities",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    root = Path(args.repo).resolve()

    failures: list[str] = []
    for rel, needles in EXPECTED.items():
        path = root / rel
        if not path.exists():
            failures.append(f"missing file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                failures.append(f"expected not found in {rel}: {needle}")
        for needle in FORBIDDEN.get(rel, []):
            if needle in text:
                failures.append(f"forbidden legacy import still present in {rel}: {needle}")

    shim = root / "app" / "config" / "runtime.py"
    if shim.exists():
        failures.append("forbidden shim exists: app/config/runtime.py")

    if failures:
        print("RC2_VALIDATION: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("RC2_VALIDATION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
