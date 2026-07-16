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

from app.runtime.document_artifact_intent import (
    build_document_artifact_payload,
    classify_document_artifact_request,
)


def test_chat_plan_detects_explicit_spreadsheet_generation_request():
    message = "vc consegue gerar uma planilha de teste, por favor"
    decision = classify_document_artifact_request(message, agent_slug="orkio")

    assert decision["handled"] is True
    assert decision["format"] == "xlsx"

    plan = build_document_artifact_payload(
        message,
        decision,
        thread_id=None,
        requested_agent_hint="orkio",
    )

    assert plan["format"] == "xlsx"
    assert plan["title"] == "Planilha de teste"
    assert plan["rows"]
    assert plan["rows"][0] == ["Item", "Descrição", "Status", "Observação"]


def test_chat_plan_does_not_generate_for_readonly_spreadsheet_analysis():
    decision = classify_document_artifact_request(
        "por favor, analise o arquivo em Excel que acabei de subir",
        agent_slug="orkio",
    )

    assert decision["handled"] is False
    assert decision["reason"] == "no_explicit_creation_verb"
