"""Validate the Python namespace required by the Orkio production bootstrap."""

from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Final


REQUIRED_MODULE: Final[str] = "app.runtime.direct_chat_persistence"
REQUIRED_CALLABLE: Final[str] = "persist_direct_assistant_message"
REPOSITORY_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
PACKAGE_PARENT: Final[Path] = REPOSITORY_ROOT.parent


def _normalized_sys_path() -> set[str]:
    """Resolve sys.path entries, including the empty current-directory entry."""
    normalized: set[str] = set()
    for entry in sys.path:
        candidate = entry or os.getcwd()
        try:
            normalized.add(str(Path(candidate).resolve()))
        except Exception:
            continue
    return normalized


def _validate_required_paths() -> None:
    """Fail with an actionable error if package and legacy roots are missing."""
    normalized = _normalized_sys_path()
    required = {str(PACKAGE_PARENT.resolve()), str(REPOSITORY_ROOT.resolve())}
    missing = sorted(required - normalized)
    if missing:
        raise RuntimeError(
            "python_namespace_required_paths_missing:" + ",".join(missing)
        )


def _find_spec(module_name: str):
    """Return a module spec without masking the underlying import error."""
    return importlib.util.find_spec(module_name)


def _load_module(module_name: str) -> ModuleType:
    """Import and return a required module."""
    return importlib.import_module(module_name)


def main() -> int:
    print("PYTHON_NAMESPACE_PREFLIGHT_START", flush=True)
    print(f"python_executable={sys.executable!r}", flush=True)
    print(f"working_sys_path={sys.path!r}", flush=True)
    print(f"repository_root={str(REPOSITORY_ROOT)!r}", flush=True)
    print(f"package_parent={str(PACKAGE_PARENT)!r}", flush=True)

    _validate_required_paths()

    app_spec = _find_spec("app")
    runtime_spec = _find_spec("app.runtime")
    persistence_spec = _find_spec(REQUIRED_MODULE)

    print(f"app_spec={app_spec!r}", flush=True)
    print(f"runtime_spec={runtime_spec!r}", flush=True)
    print(f"persistence_spec={persistence_spec!r}", flush=True)

    if app_spec is None:
        raise RuntimeError("app_package_not_found")

    if runtime_spec is None:
        raise RuntimeError("app_runtime_package_not_found")

    if persistence_spec is None:
        raise RuntimeError(
            "app_runtime_direct_chat_persistence_not_found"
        )

    module = _load_module(REQUIRED_MODULE)
    persistence_function = getattr(module, REQUIRED_CALLABLE, None)

    if not callable(persistence_function):
        raise RuntimeError(
            "persist_direct_assistant_message_not_callable"
        )

    print(
        "PYTHON_NAMESPACE_PREFLIGHT_OK "
        f"app_origin={app_spec.origin!r} "
        f"runtime_origin={runtime_spec.origin!r} "
        f"persistence_origin={persistence_spec.origin!r}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
