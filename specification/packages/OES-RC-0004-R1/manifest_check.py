#!/usr/bin/env python3
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "specification" / "packages" / "OES-RC-0004-R1"
manifest = PKG / "OES-RC-0004-R1_MANIFEST_SHA256.txt"

errors = []
for line in manifest.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    expected, rel = line.split("  ", 1)
    path = ROOT / rel
    if not path.exists():
        errors.append(f"missing: {rel}")
        continue
    actual = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    if actual != expected:
        errors.append(f"hash mismatch: {rel} expected={expected} actual={actual}")

if errors:
    print("FAIL")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("PASS: manifest hashes verified")
