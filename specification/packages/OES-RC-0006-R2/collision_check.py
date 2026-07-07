#!/usr/bin/env python3
from pathlib import Path
import hashlib
import sys

EXPECTED_OES007_SHA256 = "C67F471AAA59D0EAF57F791ED43679D0714D990903CC927A4FAE18DCD8A88B26"
EXPECTED_OES008_SHA256 = "7C316C9D218E111CD486A9E40BFD48A3E0C61B859B3D0E9F6D6C2AFBDB9552CD"
REQUIRED_OES007_PACKAGE = "specification/packages/OES-RC-0004-R1"
REQUIRED_OES008_PACKAGE = "specification/packages/OES-RC-0005-R4"
NEW_DOC = "specification/OES-009_HANDLER_BOUNDARY_RUNTIME_MAPPING.md"
NEW_PACKAGE = "specification/packages/OES-RC-0006-R2"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def require_file_sha(baseline: Path, rel: str, expected: str, label: str):
    target = baseline / Path(rel).as_posix()
    if not target.exists():
        return [f"Missing {label} baseline document: {rel}"]
    actual = sha256(target)
    if actual != expected:
        return [f"{label} baseline SHA mismatch: expected={expected} actual={actual}"]
    return []

def require_dir(baseline: Path, rel: str, label: str):
    target = baseline / Path(rel).as_posix()
    if not target.exists() or not target.is_dir():
        return [f"Missing {label} baseline package: {rel}"]
    return []

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
    errors += require_file_sha(baseline, "specification/OES-007_CONTRACT_EVENT_PROJECTION.md", EXPECTED_OES007_SHA256, "OES-007")
    errors += require_dir(baseline, REQUIRED_OES007_PACKAGE, "OES-007")
    errors += require_file_sha(baseline, "specification/OES-008_FOUNDER_CONTEXT_TRIAGE_USAGE_GOVERNANCE.md", EXPECTED_OES008_SHA256, "OES-008")
    errors += require_dir(baseline, REQUIRED_OES008_PACKAGE, "OES-008")

    if (baseline / NEW_DOC).exists():
        errors.append(f"OES-009 already exists in target: {NEW_DOC}")
    if (baseline / NEW_PACKAGE).exists():
        errors.append(f"OES-RC-0006-R2 already exists in target: {NEW_PACKAGE}")

    if errors:
        print("collision_check: FAIL")
        for error in errors:
            print(error)
        return 1

    print("collision_check: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
