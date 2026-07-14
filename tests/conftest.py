from __future__ import annotations

import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
existing = sys.modules.get("app")
if existing is None:
    existing = types.ModuleType("app")
    existing.__path__ = []  # type: ignore[attr-defined]
    sys.modules["app"] = existing

paths = list(getattr(existing, "__path__", []))
for candidate in (str(ROOT / "app"), str(ROOT)):
    if candidate not in paths:
        paths.append(candidate)
existing.__path__ = paths  # type: ignore[attr-defined]
