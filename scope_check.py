#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "specification" / "packages" / "OES-RC-0005-R4"
METADATA = PKG / "OES-RC-0005-R4_PACKAGE_METADATA.yaml"

def rel_posix(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

def main() -> int:
    errors = []
    for path in PKG.rglob("*"):
        if not path.is_file():
            continue
        rel = rel_posix(path)
        if "__pycache__" in path.parts:
            errors.append(f"Cache file found: {rel}")
        if path.suffix in {".pyc", ".pyo"}:
            errors.append(f"Compiled artifact found: {rel}")
        if not rel.startswith("specification/"):
            errors.append(f"File outside specification: {rel}")
    metadata = METADATA.read_text(encoding="utf-8")
    required = [
        "runtime_changes: false",
        "api_changes: false",
        "database_changes: false",
        "infrastructure_changes: false",
        "specification_only: true",
        "raw_private_content_included: false",
        "google_drive_raw_content_included: false",
        "chatgpt_export_raw_content_included: false",
        "source_candidate_content_access_allowed: false",
        "raw_private_content_allowed_for_learning: false",
        "learn_from_operational_metadata_only: true",
    ]
    for item in required:
        if item not in metadata:
            errors.append(f"Missing or incorrect metadata line: {item}")
    if errors:
        print("scope_check: FAIL")
        for err in errors:
            print(err)
        return 1
    print("scope_check: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
