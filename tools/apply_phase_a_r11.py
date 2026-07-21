from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


PATCH_ID = "ORKIO-AUTOEVOLUTION-PHASE-A-R1.1"
MANIFEST_NAME = "PATCH_MANIFEST.json"


class ApplyError(RuntimeError):
    pass


@dataclass(frozen=True)
class OriginalFile:
    existed: bool
    data: bytes = b""
    mode: int = 0o644


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def _safe_relative_path(raw: str) -> Path:
    rel = Path(str(raw or ""))
    if not raw or rel.is_absolute() or ".." in rel.parts:
        raise ApplyError(f"unsafe_package_path:{raw!r}")
    return rel


def load_manifest(package_root: Path) -> Dict[str, object]:
    path = package_root / MANIFEST_NAME
    if not path.is_file():
        raise ApplyError(f"manifest_missing:{path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ApplyError(f"manifest_invalid:{exc.__class__.__name__}") from exc
    if manifest.get("patch_id") != PATCH_ID:
        raise ApplyError("manifest_patch_id_mismatch")
    return manifest


def validate_payload(
    package_root: Path,
    copy_paths: Sequence[str],
    expected_hashes: Mapping[str, str],
) -> Dict[str, str]:
    observed: Dict[str, str] = {}
    for raw in copy_paths:
        rel = _safe_relative_path(raw)
        source = package_root / rel
        if not source.is_file():
            raise ApplyError(f"source_missing:{rel.as_posix()}")
        digest = sha256_path(source)
        expected = str(expected_hashes.get(rel.as_posix()) or "")
        if not expected:
            raise ApplyError(f"source_hash_missing:{rel.as_posix()}")
        if digest != expected:
            raise ApplyError(f"source_hash_mismatch:{rel.as_posix()}")
        observed[rel.as_posix()] = digest
    return observed


def _write_replace(destination: Path, data: bytes, mode: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.phase-a-r11.",
        dir=str(destination.parent),
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_path, stat.S_IMODE(mode) or 0o644)
        os.replace(temp_path, destination)
    finally:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception:
            pass


def transactional_apply(
    package_root: Path,
    target_root: Path,
    *,
    copy_paths: Sequence[str],
    expected_hashes: Mapping[str, str],
    simulate_failure_after: int = 0,
) -> Dict[str, str]:
    """Apply all files or restore every destination to its original state."""
    package_root = package_root.resolve()
    target_root = target_root.resolve()
    if not target_root.is_dir():
        raise ApplyError(f"target_not_directory:{target_root}")

    observed = validate_payload(package_root, copy_paths, expected_hashes)
    originals: Dict[str, OriginalFile] = {}
    staged: Dict[str, bytes] = {}
    created_parents: List[Path] = []

    for raw in copy_paths:
        rel = _safe_relative_path(raw)
        source = package_root / rel
        destination = target_root / rel
        try:
            destination.relative_to(target_root)
        except ValueError as exc:
            raise ApplyError(f"destination_outside_target:{rel}") from exc

        staged[rel.as_posix()] = source.read_bytes()
        if destination.exists():
            if not destination.is_file():
                raise ApplyError(f"destination_not_file:{rel.as_posix()}")
            originals[rel.as_posix()] = OriginalFile(
                existed=True,
                data=destination.read_bytes(),
                mode=stat.S_IMODE(destination.stat().st_mode),
            )
        else:
            originals[rel.as_posix()] = OriginalFile(existed=False)
            parent = destination.parent
            while parent != target_root and not parent.exists():
                created_parents.append(parent)
                parent = parent.parent

    applied: List[str] = []
    try:
        for raw in copy_paths:
            rel = _safe_relative_path(raw)
            key = rel.as_posix()
            destination = target_root / rel
            source_mode = stat.S_IMODE((package_root / rel).stat().st_mode)
            _write_replace(destination, staged[key], source_mode)
            applied.append(key)
            if simulate_failure_after and len(applied) >= simulate_failure_after:
                raise ApplyError("simulated_failure")

        for raw in copy_paths:
            rel = _safe_relative_path(raw)
            key = rel.as_posix()
            destination = target_root / rel
            if not destination.is_file():
                raise ApplyError(f"post_apply_missing:{key}")
            if sha256_path(destination) != observed[key]:
                raise ApplyError(f"post_apply_hash_mismatch:{key}")
        return observed
    except Exception as exc:
        rollback_errors: List[str] = []
        for raw in reversed(copy_paths):
            rel = _safe_relative_path(raw)
            key = rel.as_posix()
            destination = target_root / rel
            original = originals[key]
            try:
                if original.existed:
                    _write_replace(destination, original.data, original.mode)
                elif destination.exists():
                    destination.unlink()
            except Exception as rollback_exc:
                rollback_errors.append(
                    f"{key}:{rollback_exc.__class__.__name__}"
                )

        for parent in sorted(set(created_parents), key=lambda p: len(p.parts), reverse=True):
            try:
                parent.rmdir()
            except OSError:
                pass

        for raw in copy_paths:
            rel = _safe_relative_path(raw)
            key = rel.as_posix()
            destination = target_root / rel
            original = originals[key]
            try:
                if original.existed:
                    if not destination.is_file():
                        rollback_errors.append(f"{key}:missing_after_rollback")
                    elif sha256_path(destination) != sha256_bytes(original.data):
                        rollback_errors.append(f"{key}:hash_after_rollback")
                elif destination.exists():
                    rollback_errors.append(f"{key}:unexpected_after_rollback")
            except Exception as verify_exc:
                rollback_errors.append(
                    f"{key}:verify_{verify_exc.__class__.__name__}"
                )

        if rollback_errors:
            raise ApplyError(
                "apply_failed_and_rollback_incomplete:"
                + ",".join(sorted(set(rollback_errors)))
            ) from exc
        raise ApplyError(
            f"apply_failed_rollback_complete:{exc.__class__.__name__}"
        ) from exc


def _baseline_state(
    target_root: Path,
    *,
    accepted_main_hashes: Sequence[str],
    candidate_main_hash: str,
) -> Tuple[str, str]:
    main_path = target_root / "main.py"
    if not main_path.is_file():
        raise ApplyError("target_main_missing")
    observed = sha256_path(main_path)
    if observed == candidate_main_hash:
        return "already_candidate", observed
    if observed not in set(accepted_main_hashes):
        raise ApplyError(f"unknown_main_baseline:{observed}")
    return "accepted_baseline", observed


def execute(
    target_root: Path,
    *,
    package_root: Optional[Path] = None,
    dry_run: bool = False,
    simulate_failure_after: int = 0,
) -> Dict[str, object]:
    root = Path(package_root or Path(__file__).resolve().parents[1]).resolve()
    target = target_root.resolve()
    manifest = load_manifest(root)
    copy_paths = [str(value) for value in manifest.get("copy_paths", [])]
    expected_hashes = {
        str(key): str(value)
        for key, value in dict(manifest.get("payload_sha256", {})).items()
    }
    accepted = [
        str(value)
        for value in manifest.get("accepted_source_main_sha256", [])
    ]
    candidate_hash = str(manifest.get("candidate_main_sha256") or "")
    if not copy_paths or not candidate_hash:
        raise ApplyError("manifest_apply_contract_incomplete")

    baseline_state, observed_main = _baseline_state(
        target,
        accepted_main_hashes=accepted,
        candidate_main_hash=candidate_hash,
    )
    payload = validate_payload(root, copy_paths, expected_hashes)

    if baseline_state == "already_candidate":
        mismatches = [
            rel
            for rel, expected in payload.items()
            if not (target / rel).is_file()
            or sha256_path(target / rel) != expected
        ]
        if not mismatches:
            return {
                "ok": True,
                "patch_id": PATCH_ID,
                "mode": "already_applied",
                "write_executed": False,
                "rollback_executed": False,
                "observed_main_sha256": observed_main,
                "candidate_main_sha256": candidate_hash,
            }

    if dry_run:
        return {
            "ok": True,
            "patch_id": PATCH_ID,
            "mode": "dry_run",
            "baseline_state": baseline_state,
            "write_executed": False,
            "rollback_executed": False,
            "observed_main_sha256": observed_main,
            "candidate_main_sha256": candidate_hash,
            "copy_count": len(copy_paths),
        }

    transactional_apply(
        root,
        target,
        copy_paths=copy_paths,
        expected_hashes=expected_hashes,
        simulate_failure_after=simulate_failure_after,
    )
    return {
        "ok": True,
        "patch_id": PATCH_ID,
        "mode": "applied",
        "write_executed": True,
        "rollback_executed": False,
        "observed_main_sha256": observed_main,
        "candidate_main_sha256": candidate_hash,
        "copy_count": len(copy_paths),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fail-closed transactional applier for ORKIO Phase A R1.1"
    )
    parser.add_argument("target", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--simulate-failure-after",
        type=int,
        default=0,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)
    try:
        result = execute(
            args.target,
            dry_run=args.dry_run,
            simulate_failure_after=max(0, args.simulate_failure_after),
        )
        print(json.dumps(result, sort_keys=True))
        return 0
    except ApplyError as exc:
        print(
            json.dumps(
                {
                    "ok": False,
                    "patch_id": PATCH_ID,
                    "error": str(exc),
                    "write_executed": False,
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
