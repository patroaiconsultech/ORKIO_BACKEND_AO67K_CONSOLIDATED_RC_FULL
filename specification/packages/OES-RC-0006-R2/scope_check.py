#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
MANIFEST = PACKAGE / "OES-RC-0006-R2_MANIFEST_SHA256.txt"

FORBIDDEN_PARTS = {"__pycache__", ".git"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".zip"}

def main() -> int:
    errors = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        _, rel = line.split("  ", 1)
        rel_posix = Path(rel.strip()).as_posix()
        p = Path(rel_posix)
        if not rel_posix.startswith("specification/"):
            errors.append(f"Path outside specification: {rel_posix}")
        if any(part in FORBIDDEN_PARTS for part in p.parts):
            errors.append(f"Forbidden path component: {rel_posix}")
        if p.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"Forbidden suffix: {rel_posix}")
    if errors:
        print("scope_check: FAIL")
        for e in errors:
            print(e)
        return 1
    print("scope_check: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
