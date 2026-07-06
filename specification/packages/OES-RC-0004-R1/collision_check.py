#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()
PKG = ROOT / "specification" / "packages" / "OES-RC-0004-R1"
manifest = PKG / "OES-RC-0004-R1_MANIFEST_SHA256.txt"

errors = []
for line in manifest.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    _, rel = line.split("  ", 1)
    if rel.startswith("/") or ".." in Path(rel).parts:
        errors.append(f"unsafe path: {rel}")
    if not rel.startswith("specification/"):
        errors.append(f"path outside specification: {rel}")

for path in ROOT.rglob("*"):
    if path.is_file():
        parts = set(path.parts)
        name = path.name
        if "__pycache__" in parts or name.endswith((".pyc", ".pyo")):
            continue
        if str(path.relative_to(ROOT)).startswith("specification/packages/OES-RC-0004-R1/") or str(path.relative_to(ROOT)) == "specification/OES-007_CONTRACT_EVENT_PROJECTION.md":
            continue

if errors:
    print("FAIL")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("PASS: all OES-RC-0004-R1 paths remain under specification")
