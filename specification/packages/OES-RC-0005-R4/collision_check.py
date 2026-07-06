#!/usr/bin/env python3
from pathlib import Path
import hashlib, sys, json

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "specification" / "packages" / "OES-RC-0005-R4"
EXPECTED = PKG / "expected_added_paths.json"

EXPECTED_BASELINE_DOC_REL = Path("specification/OES-007_CONTRACT_EVENT_PROJECTION.md")
EXPECTED_BASELINE_DOC_SHA256 = "C67F471AAA59D0EAF57F791ED43679D0714D990903CC927A4FAE18DCD8A88B26"
EXPECTED_BASELINE_PACKAGE_REL = Path("specification/packages/OES-RC-0004-R1")
FORBIDDEN_PREEXISTING_REL = [
    Path("specification/OES-008_FOUNDER_CONTEXT_TRIAGE_USAGE_GOVERNANCE.md"),
    Path("specification/packages/OES-RC-0005-R4"),
]

def rel_to_str(path: Path) -> str:
    return path.as_posix()

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def fail(errors) -> int:
    print("collision_check: FAIL")
    for err in errors:
        print(err)
    return 1

def main() -> int:
    errors = []
    if len(sys.argv) != 2:
        print("collision_check: FAIL")
        print("Usage: collision_check.py /path/to/baseline_repo_root")
        print("A baseline root is required; this check must not pass nominally.")
        return 1

    baseline = Path(sys.argv[1]).resolve()
    if not baseline.exists() or not baseline.is_dir():
        return fail([f"Baseline root does not exist or is not a directory: {baseline}"])

    baseline_doc = baseline / EXPECTED_BASELINE_DOC_REL
    if not baseline_doc.exists() or not baseline_doc.is_file():
        errors.append(f"Baseline identity missing: {rel_to_str(EXPECTED_BASELINE_DOC_REL)}")
    elif sha256(baseline_doc) != EXPECTED_BASELINE_DOC_SHA256:
        errors.append(
            "Baseline identity mismatch for "
            f"{rel_to_str(EXPECTED_BASELINE_DOC_REL)}: expected {EXPECTED_BASELINE_DOC_SHA256}, got {sha256(baseline_doc)}"
        )

    baseline_pkg = baseline / EXPECTED_BASELINE_PACKAGE_REL
    if not baseline_pkg.exists() or not baseline_pkg.is_dir():
        errors.append(f"Baseline RC package missing: {rel_to_str(EXPECTED_BASELINE_PACKAGE_REL)}")

    for rel in FORBIDDEN_PREEXISTING_REL:
        if (baseline / rel).exists():
            errors.append(f"Target baseline already contains OES-008/R4 path: {rel_to_str(rel)}")

    if errors:
        return fail(errors)

    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    for item in expected.get("added_paths", []):
        rel = Path(item["path"])
        rel_posix = rel.as_posix()
        current = ROOT / rel
        previous = baseline / rel
        if not current.exists():
            errors.append(f"Expected current file missing: {rel_posix}")
            continue
        if sha256(current) != item["sha256"]:
            errors.append(f"Current hash mismatch for {rel_posix}")
        if previous.exists():
            if sha256(previous) != sha256(current):
                errors.append(f"Collision/overwrite risk: target baseline already has different file: {rel_posix}")
            else:
                errors.append(f"Path already exists in baseline; not an added file: {rel_posix}")
        if not rel_posix.startswith("specification/"):
            errors.append(f"Path outside specification: {rel_posix}")

    if errors:
        return fail(errors)
    print("collision_check: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
