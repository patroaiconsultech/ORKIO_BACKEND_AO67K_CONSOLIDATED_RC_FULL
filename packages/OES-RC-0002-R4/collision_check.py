from pathlib import Path
import sys

if len(sys.argv) != 3:
    raise SystemExit("usage: collision_check.py <staging> <target_repo>")

staging = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2]).resolve()

if not staging.exists():
    raise SystemExit(f"staging does not exist: {staging}")
if not target.exists():
    raise SystemExit(f"target repo does not exist: {target}")

allowed_new_prefixes = [
    "specification/packages/OES-RC-0002-R4/",
]
allowed_new_files = {
    "specification/OES-005_CANONICAL_DOMAIN_MODEL.md",
}

intentional_replacements = set()
collisions = []
unsafe = []

for path in staging.rglob("*"):
    if not path.is_file():
        continue
    rel = path.relative_to(staging).as_posix()
    if not rel.startswith("specification/"):
        unsafe.append(rel)
        continue
    dest = (target / rel).resolve(strict=False)
    try:
        dest.relative_to(target)
    except ValueError:
        unsafe.append(rel)
        continue
    exists = dest.exists()
    allowed = rel in allowed_new_files or any(rel.startswith(prefix) for prefix in allowed_new_prefixes)
    if exists and rel not in intentional_replacements:
        collisions.append(rel)
    if not allowed and not exists:
        unsafe.append(rel)

if unsafe:
    raise SystemExit("UNSAFE TARGET PATHS\n" + "\n".join(sorted(unsafe)))
if collisions:
    raise SystemExit("COLLISION CHECK FAIL\n" + "\n".join(sorted(collisions)))

print("COLLISION CHECK PASS")
