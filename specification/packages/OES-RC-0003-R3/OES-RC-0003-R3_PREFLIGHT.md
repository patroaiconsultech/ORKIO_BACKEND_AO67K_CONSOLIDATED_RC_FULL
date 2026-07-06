# OES-RC-0003-R3 — Preflight

## Required Flow

This package MUST be installed through an isolated staging flow.

1. Inspect ZIP entries before any extraction.
2. Reject unsafe paths, absolute paths, traversal, empty segments, duplicate normalized destinations, symlinks and non-regular files.
3. Extract only into an isolated staging directory.
4. Run package hygiene gate in staging.
5. Run coverage check in staging.
6. Run collision check against the target repository.
7. Validate SHA-256 manifest in staging.
8. Copy to repository only after all gates pass.

## Inputs

```bash
ZIP="OES-RC-0003-R3_CAPABILITY_CATALOG_REPO_READY.zip"
TARGET_REPO="/path/to/ORKIO_BACKEND_AO67K_CONSOLIDATED_RC_FULL"
STAGING="$(mktemp -d)"
```

## Gate 1 — Pre-Extraction ZIP Inspection

Run this BEFORE `unzip`.

```bash
python - "$ZIP" "$STAGING" <<'PY'
from __future__ import annotations

import os
from pathlib import Path
import stat
import sys
import zipfile

zip_path = Path(sys.argv[1]).resolve()
staging = Path(sys.argv[2]).resolve()
destinations: set[str] = set()

def fail(message: str) -> None:
    print(f"ZIP PREFLIGHT FAIL: {message}")
    raise SystemExit(1)

with zipfile.ZipFile(zip_path) as zf:
    for info in zf.infolist():
        name = info.filename

        if not name:
            fail("empty ZIP entry name")
        if "\\" in name:
            fail(f"backslash path separator is not allowed: {name}")
        if not name.startswith("specification/"):
            fail(f"entry outside specification/: {name}")
        if name.startswith("/") or (len(name) > 1 and name[1] == ":"):
            fail(f"absolute path is not allowed: {name}")
        if "//" in name or name.endswith("/.") or "/./" in name:
            fail(f"empty or dot segment is not allowed: {name}")
        parts = name.split("/")
        if any(part in ("", ".", "..") for part in parts):
            fail(f"unsafe path segment: {name}")

        mode = (info.external_attr >> 16) & 0o170000
        if name.endswith("/"):
            # Directory entries are allowed only inside specification/.
            continue
        if mode and stat.S_ISLNK(mode):
            fail(f"symlink entry is not allowed: {name}")
        if mode and not stat.S_ISREG(mode):
            fail(f"non-regular entry is not allowed: {name}")

        destination = (staging / name).resolve()
        try:
            destination.relative_to(staging)
        except ValueError:
            fail(f"resolved destination escapes staging: {name}")

        key = os.path.normcase(str(destination))
        if key in destinations:
            fail(f"duplicate normalized destination: {name}")
        destinations.add(key)

print("ZIP PREFLIGHT PASS")
PY
```

## Gate 2 — Isolated Extraction

```bash
unzip "$ZIP" -d "$STAGING"
cd "$STAGING"
```

## Gate 3 — Package Hygiene

```bash
if find specification -type d -name '__pycache__' -o \
        -type f \( -name '*.pyc' -o -name '*.pyo' \) | grep .; then
  echo "PACKAGE FAIL: cache or compiled files"
  exit 1
fi
```

## Gate 4 — Coverage + Vocabulary Check

```bash
python specification/packages/OES-RC-0003-R3/coverage_check.py
```

## Gate 5 — Collision Check with Preimage Hash Verification

```bash
python specification/packages/OES-RC-0003-R3/collision_check.py "$TARGET_REPO"
```

The only allowed replacement is:

```text
specification/OES-006_CAPABILITY_CATALOG.md
```

This replacement is permitted only when the target file hash matches one of the declared OES-006 preimages:

```text
3391510CF4F03C95B4793ACD063FAC430CE6B367480473AAC92DEA7D97091684
B3267359FE6BF3B07C28F390EF963814AA2EE40A860361048368E68CD972ABE6
```

All other collisions MUST fail.

## Gate 6 — Manifest Validation

```bash
sha256sum -c specification/packages/OES-RC-0003-R3/OES-RC-0003-R3_MANIFEST_SHA256.txt
```

## Gate 7 — Conditional Copy

Copy to the target repository only after all previous gates return PASS.

```bash
rsync -a specification/ "$TARGET_REPO/specification/"
```
