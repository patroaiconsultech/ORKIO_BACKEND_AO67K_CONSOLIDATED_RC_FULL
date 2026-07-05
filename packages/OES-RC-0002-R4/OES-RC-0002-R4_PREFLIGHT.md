# OES-RC-0002-R4 — Preflight

## Purpose

Validate package safety before applying it to the target repository.

## Required Order

1. Inspect ZIP entries before extraction.
2. Reject unsafe paths and symlinks.
3. Extract to isolated staging only after validation.
4. Validate manifest in staging.
5. Run coverage checks.
6. Compare with target repository for collisions.
7. Copy only after all gates pass.

## Executable Preflight

```bash
ZIP="$1"
TARGET_REPO="${2:-}"
STAGING="$(mktemp -d)"

python - "$ZIP" "$STAGING" <<'PY'
import os
import pathlib
import stat
import sys
import zipfile

zip_path = pathlib.Path(sys.argv[1]).resolve()
staging = pathlib.Path(sys.argv[2]).resolve()
destinations = set()

with zipfile.ZipFile(zip_path) as zf:
    for info in zf.infolist():
        name = info.filename

        if (
            not name.startswith("specification/")
            or name.startswith("/")
            or ":" in pathlib.PurePosixPath(name).parts[0]
            or "\\" in name
            or ".." in pathlib.PurePosixPath(name).parts
            or "//" in name
            or "/./" in name
            or name.endswith("/.")
            or name.endswith("/")
        ):
            raise SystemExit(f"UNSAFE ZIP ENTRY: {name}")

        mode = (info.external_attr >> 16) & 0o170000
        if mode and not stat.S_ISREG(mode):
            raise SystemExit(f"UNSAFE ZIP ENTRY TYPE: {name}")

        destination = staging / pathlib.PurePosixPath(name)
        resolved = destination.resolve(strict=False)

        if staging != resolved and staging not in resolved.parents:
            raise SystemExit(f"ZIP ENTRY ESCAPES STAGING: {name}")

        key = os.path.normcase(str(resolved))
        if key in destinations:
            raise SystemExit(f"DUPLICATE ZIP DESTINATION: {name}")
        destinations.add(key)

print("PRE-EXTRACTION VALIDATION PASS")
PY

unzip -q "$ZIP" -d "$STAGING"
cd "$STAGING"
if find specification \( -type d -name '__pycache__' -o -type f \( -name '*.pyc' -o -name '*.pyo' \) \) | grep .; then
  echo "PACKAGE FAIL: cache or compiled files"
  exit 1
fi
sha256sum -c specification/packages/OES-RC-0002-R4/OES-RC-0002-R4_MANIFEST_SHA256.txt
python specification/packages/OES-RC-0002-R4/coverage_check.py

if [ -n "$TARGET_REPO" ]; then
  python specification/packages/OES-RC-0002-R4/collision_check.py "$STAGING" "$TARGET_REPO"
else
  echo "COLLISION CHECK SKIPPED: target repository path not provided"
  echo "Baseline promotion requires running collision_check.py with TARGET_REPO."
fi
```

## Collision Policy

Reject if the package would overwrite any existing file unless the replacement is explicitly declared in package metadata.

This package declares no intentional replacements.

## Cache and Compiled Artifact Gate

Packages must not contain `__pycache__/`, `*.pyc`, or `*.pyo`. Validation tooling may be included as source text only. Syntax validation must be performed in disposable staging or by in-memory compilation before packaging.
