from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from tools.apply_phase_a_r11 import ApplyError, transactional_apply


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _make_package(tmp_path: Path):
    package = tmp_path / "package"
    target = tmp_path / "target"
    package.mkdir()
    target.mkdir()

    (package / "a.txt").write_bytes(b"new-a")
    (package / "nested").mkdir()
    (package / "nested" / "b.txt").write_bytes(b"new-b")

    (target / "a.txt").write_bytes(b"old-a")
    (target / "nested").mkdir()
    (target / "nested" / "b.txt").write_bytes(b"old-b")

    copy_paths = ["a.txt", "nested/b.txt"]
    hashes = {
        "a.txt": _sha(b"new-a"),
        "nested/b.txt": _sha(b"new-b"),
    }
    return package, target, copy_paths, hashes


def test_transactional_apply_success(tmp_path):
    package, target, copy_paths, hashes = _make_package(tmp_path)
    observed = transactional_apply(
        package,
        target,
        copy_paths=copy_paths,
        expected_hashes=hashes,
    )
    assert observed == hashes
    assert (target / "a.txt").read_bytes() == b"new-a"
    assert (target / "nested" / "b.txt").read_bytes() == b"new-b"


def test_transactional_apply_restores_all_files_after_failure(tmp_path):
    package, target, copy_paths, hashes = _make_package(tmp_path)

    with pytest.raises(ApplyError) as exc:
        transactional_apply(
            package,
            target,
            copy_paths=copy_paths,
            expected_hashes=hashes,
            simulate_failure_after=1,
        )

    assert "rollback_complete" in str(exc.value)
    assert (target / "a.txt").read_bytes() == b"old-a"
    assert (target / "nested" / "b.txt").read_bytes() == b"old-b"


def test_transactional_apply_removes_new_files_after_failure(tmp_path):
    package = tmp_path / "package"
    target = tmp_path / "target"
    package.mkdir()
    target.mkdir()
    (package / "a.txt").write_bytes(b"new-a")
    (package / "newdir").mkdir()
    (package / "newdir" / "b.txt").write_bytes(b"new-b")
    copy_paths = ["a.txt", "newdir/b.txt"]
    hashes = {
        "a.txt": _sha(b"new-a"),
        "newdir/b.txt": _sha(b"new-b"),
    }

    with pytest.raises(ApplyError):
        transactional_apply(
            package,
            target,
            copy_paths=copy_paths,
            expected_hashes=hashes,
            simulate_failure_after=1,
        )

    assert not (target / "a.txt").exists()
    assert not (target / "newdir" / "b.txt").exists()
    assert not (target / "newdir").exists()


def test_unsafe_path_is_rejected(tmp_path):
    package = tmp_path / "package"
    target = tmp_path / "target"
    package.mkdir()
    target.mkdir()

    with pytest.raises(ApplyError):
        transactional_apply(
            package,
            target,
            copy_paths=["../escape.txt"],
            expected_hashes={"../escape.txt": _sha(b"x")},
        )
