#!/usr/bin/env python3
from pathlib import Path
import hashlib, sys

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "specification" / "packages" / "OES-RC-0005-R4" / "OES-RC-0005-R4_MANIFEST_SHA256.txt"

def rel_posix(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def main() -> int:
    errors = []
    seen = set()
    if not MANIFEST.exists():
        errors.append(f"Manifest missing: {rel_posix(MANIFEST) if MANIFEST.exists() else MANIFEST}")
    else:
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                expected, rel = line.split("  ", 1)
            except ValueError:
                errors.append(f"Malformed manifest line: {line}")
                continue
            rel = rel.replace("\\", "/")
            if rel in seen:
                errors.append(f"Duplicate manifest entry: {rel}")
            seen.add(rel)
            path = ROOT / rel
            if not path.exists():
                errors.append(f"Missing: {rel}")
                continue
            actual = sha256(path)
            if actual != expected:
                errors.append(f"Hash mismatch: {rel} expected={expected} actual={actual}")

    # Every file in the package except the manifest itself must be manifest-listed.
    pkg = ROOT / "specification" / "packages" / "OES-RC-0005-R4"
    targets = [ROOT / "specification" / "OES-008_FOUNDER_CONTEXT_TRIAGE_USAGE_GOVERNANCE.md", *pkg.rglob("*")]
    for path in targets:
        if path.is_file() and path != MANIFEST:
            rel = rel_posix(path)
            if rel not in seen:
                errors.append(f"File not manifest-listed: {rel}")

    if errors:
        print("manifest_check: FAIL")
        for err in errors:
            print(err)
        return 1
    print("manifest_check: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
