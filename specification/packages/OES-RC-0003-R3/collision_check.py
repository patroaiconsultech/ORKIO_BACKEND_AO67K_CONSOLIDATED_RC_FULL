#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import hashlib
import sys

PKG_ID = "OES-RC-0003-R3"

# The only allowed replacement is the prior OES-006 document.
# It is allowed only if the target file preimage hash matches one of the
# explicitly declared rejected/pre-R3 hashes below.
INTENTIONAL_REPLACEMENTS = {
    "specification/OES-006_CAPABILITY_CATALOG.md": {
        "3391510CF4F03C95B4793ACD063FAC430CE6B367480473AAC92DEA7D97091684",
        "B3267359FE6BF3B07C28F390EF963814AA2EE40A860361048368E68CD972ABE6",
    },
}

PACKAGE_PATHS = [
    "specification/OES-006_CAPABILITY_CATALOG.md",
]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def fail(message: str) -> None:
    print(f"COLLISION FAIL: {message}")
    raise SystemExit(1)

def main() -> None:
    if len(sys.argv) < 2:
        fail("target repository path is required")

    target = Path(sys.argv[1]).resolve()
    if not target.exists():
        fail(f"target repo does not exist: {target}")

    failures = []
    for rel in PACKAGE_PATHS:
        dest = target / rel
        if not dest.exists():
            continue
        if rel not in INTENTIONAL_REPLACEMENTS:
            failures.append(f"unapproved existing path: {rel}")
            continue
        allowed_hashes = INTENTIONAL_REPLACEMENTS[rel]
        actual_hash = sha256_file(dest)
        if actual_hash not in allowed_hashes:
            failures.append(
                "replacement preimage mismatch for "
                f"{rel}: expected one of {sorted(allowed_hashes)}, got {actual_hash}"
            )

    # Package control directory is unique for R3 and must not already exist.
    control_dir = target / "specification" / "packages" / PKG_ID
    if control_dir.exists():
        failures.append(str(control_dir.relative_to(target)))

    if failures:
        for item in failures:
            print(f"- {item}")
        raise SystemExit(1)

    print("COLLISION PASS")

if __name__ == "__main__":
    main()
