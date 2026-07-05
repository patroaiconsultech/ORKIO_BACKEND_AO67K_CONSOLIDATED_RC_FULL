# OES-RC-0001-R3 — Preflight

## Objective
Validate the package safely before copying any file into the target repository.

## Required Order
1. Inspect ZIP entries before extraction.
2. Reject unsafe paths, unexpected roots, and symlinks before extraction.
3. Create a temporary staging directory outside the target repository.
4. Normalize each entry destination and confirm it remains inside staging.
5. Extract only after pre-extraction validation passes.
6. Validate staged SHA-256 hashes.
7. Compare staged paths with the target repository.
8. Block unexpected collisions.
9. Copy files into the repository only after all checks pass.
10. Record audit evidence externally, in the PR, commit notes, or audit attestation.

## Manual Procedure
1. Set variables for the ZIP, staging directory, target repository, and entry list.
2. Enumerate ZIP entries without extracting.
3. Confirm every entry starts with `specification/`.
4. Confirm no entry is absolute, drive-qualified, or contains `..`.
5. Confirm no entry uses backslash traversal.
6. Confirm no symlink is present.
7. Create staging outside the target repository.
8. For every entry, normalize the target extraction path and confirm it resolves inside staging.
9. Extract the ZIP into staging.
10. Validate the SHA-256 manifest from inside staging.
11. Compare staged files against the target repository.
12. Block if an existing target file would be overwritten unexpectedly.
13. Copy the staged `specification/` tree into the repository.
14. Record validation evidence outside the ZIP package.

## Suggested Shell Checks
```bash
ZIP="OES-RC-0001-R3_ENGINEERING_FOUNDATION_REPO_READY.zip"
TARGET_REPO="/path/to/ORKIO_BACKEND_AO67K_CONSOLIDATED_RC_FULL"
STAGING="$(mktemp -d)"
ENTRIES="$(mktemp)"
VALIDATOR="$(mktemp)"

zipinfo -1 "$ZIP" > "$ENTRIES"

# Reject anything outside specification/ before extraction.
if grep -Ev '^specification/' "$ENTRIES"; then
  echo "UNSAFE ZIP: entry outside specification/"
  exit 1
fi

# Reject absolute paths, Windows drive paths, path traversal, and backslash traversal before extraction.
if grep -E '(^/|^[A-Za-z]:|(^|/)[.][.](/|$)|(^|\\)[.][.](\\|$))' "$ENTRIES"; then
  echo "UNSAFE ZIP: absolute path or traversal"
  exit 1
fi

# Reject empty or current-directory segments before extraction.
if grep -E '(^|/)(\.?)(/|$)|//' "$ENTRIES"; then
  echo "UNSAFE ZIP: empty or current-directory segment"
  exit 1
fi

# Reject symlinks before extraction. In zipinfo -l output, symlinks appear with file mode starting with l.
if zipinfo -l "$ZIP" | awk 'NR>3 && $1 ~ /^l/ {print; found=1} END {exit found ? 0 : 1}'; then
  echo "UNSAFE ZIP: symlink entry detected"
  exit 1
fi

cat > "$VALIDATOR" <<'PY'
import os
import pathlib
import sys
import zipfile

zip_path = pathlib.Path(sys.argv[1])
staging = pathlib.Path(sys.argv[2]).resolve(strict=False)
destinations = set()

with zipfile.ZipFile(zip_path) as zf:
    for info in zf.infolist():
        name = info.filename

        # Validate the original ZIP entry string before pathlib can normalize it.
        if (
            not name.startswith("specification/")
            or name.startswith("/")
            or "\\" in name
            or "//" in name
            or "/./" in name
            or name.endswith("/.")
            or (len(name) >= 2 and name[1] == ":")
        ):
            raise SystemExit(f"UNSAFE ZIP ENTRY: {name}")

        normalized = pathlib.PurePosixPath(name)
        if (
            len(normalized.parts) == 0
            or any(part in ("", ".", "..") for part in normalized.parts)
        ):
            raise SystemExit(f"UNSAFE ZIP ENTRY: {name}")

        mode = (info.external_attr >> 16) & 0o170000
        if mode == 0o120000:
            raise SystemExit(f"UNSAFE ZIP SYMLINK: {name}")

        destination = (staging / pathlib.Path(*normalized.parts)).resolve(strict=False)

        # Premium hardening: confirm the resolved destination remains inside staging.
        if destination != staging and staging not in destination.parents:
            raise SystemExit(f"UNSAFE ZIP DESTINATION: {name} -> {destination}")

        key = os.path.normcase(str(destination))
        if key in destinations:
            raise SystemExit(f"DUPLICATE ZIP DESTINATION: {name} -> {destination}")
        destinations.add(key)
PY

# The validator must compile before it can gate extraction.
python3 -m py_compile "$VALIDATOR"
python3 "$VALIDATOR" "$ZIP" "$STAGING"

# Only after all pre-extraction checks pass:
unzip "$ZIP" -d "$STAGING"

cd "$STAGING"

find specification -type f | sort

sha256sum -c specification/packages/OES-RC-0001-R3/OES-RC-0001-R3_MANIFEST_SHA256.txt

while IFS= read -r file; do
  if [ -e "$TARGET_REPO/$file" ]; then
    echo "COLLISION: $file"
    exit 1
  fi
done < <(find specification -type f | sort)

cp -R specification "$TARGET_REPO/"
```

## Evidence Rule
The ZIP SHA-256 is not recorded inside this ZIP because rebuilding the ZIP changes its own hash. Record ZIP SHA-256 externally in the audit report, PR description, commit message, or release attestation.

## Expected Result
Preflight passes only when ZIP entries are safe before extraction, all hashes are valid in staging, and no unexpected target collision exists.
