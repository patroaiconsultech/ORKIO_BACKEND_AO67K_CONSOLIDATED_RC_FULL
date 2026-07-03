from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import apply_shadow_candidate as asc


class Result:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def test_ensure_expected_git_sha_accepts_locked_baseline(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        return Result(stdout=asc.EXPECTED_BASELINE_SHA + "\n", returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    asc.ensure_expected_git_sha(tmp_path)


def test_ensure_expected_git_sha_rejects_mismatch(monkeypatch, tmp_path):
    def fake_run(*args, **kwargs):
        return Result(stdout="0000000000000000000000000000000000000000\n", returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    try:
        asc.ensure_expected_git_sha(tmp_path)
    except asc.ApplyError as exc:
        assert "baseline SHA mismatch" in str(exc)
    else:
        raise AssertionError("expected baseline SHA mismatch")


def test_skip_sha_check_argument_is_not_available():
    assert "--skip-sha-check" not in Path(asc.__file__).read_text(encoding="utf-8")


def test_forbidden_preexisting_shim_is_rejected_before_apply(tmp_path):
    shim = tmp_path / "app" / "config" / "runtime.py"
    shim.parent.mkdir(parents=True)
    shim.write_text("RUNTIME_FLAGS = {}\n", encoding="utf-8")

    try:
        asc.ensure_no_forbidden_preexisting_paths(tmp_path)
    except asc.ApplyError as exc:
        assert "forbidden pre-existing shim/path" in str(exc)
        assert "app/config/runtime.py" in str(exc)
    else:
        raise AssertionError("expected forbidden pre-existing shim rejection")
