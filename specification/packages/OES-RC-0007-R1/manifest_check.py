#!/usr/bin/env python3
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
MANIFEST = PACKAGE / "OES-RC-0007-R1_MANIFEST_SHA256.txt"

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def main() -> int:
    ok = bad = missing = 0
    if not MANIFEST.exists():
        print("manifest_check: FAIL")
        print("Missing manifest")
        return 1
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split("  ", 1)
        rel_posix = Path(rel.strip()).as_posix()
        target = ROOT / rel_posix
        if not target.exists():
            print(f"MISSING {rel_posix}")
            missing += 1
            continue
        actual = sha256(target)
        if actual != expected.upper():
            print(f"BAD {rel_posix} expected={expected.upper()} actual={actual}")
            bad += 1
        else:
            ok += 1
    if bad or missing:
        print("manifest_check: FAIL")
        print(f"OK={ok} BAD={bad} MISSING={missing}")
        return 1
    print("manifest_check: PASS")
    print(f"OK={ok} BAD=0 MISSING=0")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
