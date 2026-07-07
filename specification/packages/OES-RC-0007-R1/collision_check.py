#!/usr/bin/env python3
from pathlib import Path
import hashlib
import sys

EXPECTED_OES009_HANDLER_MAPPING_SHA256 = "DD8FCDA6426516E6AE014B97CC127A07F86B4D37CD025A4F97E4752D8AFF60BD"
REQUIRED_OES009_PACKAGE = "specification/packages/OES-RC-0006-R2"
NEW_DOC = "specification/OES-010_PERSISTENCE_AND_STATE_MODEL.md"
NEW_PACKAGE = "specification/packages/OES-RC-0007-R1"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def main() -> int:
    if len(sys.argv) != 2:
        print("usage: collision_check.py <baseline_repo_dir>")
        return 2

    baseline = Path(sys.argv[1]).resolve()
    if not baseline.exists() or not baseline.is_dir():
        print("collision_check: FAIL")
        print("Baseline directory does not exist")
        return 1

    errors = []
    mapping = baseline / "specification/packages/OES-RC-0006-R2/handler_boundary_mapping.json"
    if not mapping.exists():
        errors.append("Missing OES-009 handler_boundary_mapping.json")
    else:
        actual = sha256(mapping)
        if actual != EXPECTED_OES009_HANDLER_MAPPING_SHA256:
            errors.append(f"OES-009 handler mapping SHA mismatch: expected={EXPECTED_OES009_HANDLER_MAPPING_SHA256} actual={actual}")

    if not (baseline / REQUIRED_OES009_PACKAGE).exists():
        errors.append(f"Missing OES-009 baseline package: {REQUIRED_OES009_PACKAGE}")

    if (baseline / NEW_DOC).exists():
        errors.append(f"OES-010 already exists in target: {NEW_DOC}")
    if (baseline / NEW_PACKAGE).exists():
        errors.append(f"OES-RC-0007-R1 already exists in target: {NEW_PACKAGE}")

    if errors:
        print("collision_check: FAIL")
        for error in errors:
            print(error)
        return 1

    print("collision_check: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
