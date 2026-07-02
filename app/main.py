from __future__ import annotations

from pathlib import Path

_ROOT_MAIN = Path(__file__).resolve().parent.parent / "main.py"

globals()["__file__"] = str(_ROOT_MAIN)
globals()["__package__"] = "app"

exec(compile(_ROOT_MAIN.read_text(encoding="utf-8"), str(_ROOT_MAIN), "exec"), globals())
