from __future__ import annotations

import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
app_alias = sys.modules.get("app")
if app_alias is None:
    app_alias = types.ModuleType("app")
    app_alias.__path__ = [str(ROOT / "app"), str(ROOT)]  # type: ignore[attr-defined]
    sys.modules["app"] = app_alias

from app.main import _docio_chat_artifact_plan


def test_chat_plan_detects_explicit_spreadsheet_generation_request():
    plan = _docio_chat_artifact_plan("vc consegue gerar uma planilha de teste, por favor")

    assert plan is not None
    assert plan["format"] == "xlsx"
    assert plan["title"] == "Planilha de teste"
    assert plan["rows"][0] == ["Campo", "Valor"]


def test_chat_plan_does_not_generate_for_readonly_spreadsheet_analysis():
    plan = _docio_chat_artifact_plan("por favor, analise o arquivo em Excel que acabei de subir")

    assert plan is None

