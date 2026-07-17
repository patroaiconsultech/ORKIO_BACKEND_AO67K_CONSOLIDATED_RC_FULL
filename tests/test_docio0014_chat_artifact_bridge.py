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
    DOCIO0018_BRIDGE_GOVERNANCE_GUARD_VERSION,
    DOCIO003_SOURCE_BINDING_VERSION,
    DOCIO004_PPTX_SOURCE_QUALITY_VERSION,
    DOCIO005_PREMIUM_SOURCE_CONTRACT_VERSION,
    build_document_artifact_payload,
    classify_document_artifact_request,
    has_document_artifact_write_blocker,
    source_binding_unavailable_message,
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


def test_chat_plan_detects_direct_pptx_extension_generation_request():
    decision = classify_document_artifact_request(
        "Por favor, agora gere um pptx com as mesmas informacoes",
        agent_slug="orkio",
    )

    assert decision["handled"] is True
    assert decision["format"] == "pptx"


def test_chat_plan_detects_direct_docx_and_pdf_extension_generation_requests():
    docx = classify_document_artifact_request(
        "gere um docx executivo, por favor",
        agent_slug="orion",
    )
    pdf = classify_document_artifact_request(
        "gere um pdf executivo, por favor",
        agent_slug="orion",
    )

    assert docx["handled"] is True
    assert docx["format"] == "docx"
    assert pdf["handled"] is True
    assert pdf["format"] == "pdf"


def test_chat_plan_blocks_artifact_generation_under_explicit_governance_guards():
    message = (
        "Orion, ajuste o Orkio e suas respostas. "
        "Modo observe_only e proposal_only. "
        "Nao escreva arquivo, nao gere artefato, nao crie branch, "
        "nao faca commit, nao faca deploy. "
        "Entregue somente uma proposta textual."
    )

    decision = classify_document_artifact_request(message, agent_slug="orion")

    assert decision["handled"] is False
    assert decision["reason"] == "governance_write_blocked"
    assert decision["write_executed"] is False
    assert decision["artifact_created"] is False
    assert decision["proposal_only"] is True
    assert decision["observe_only"] is True
    assert "capability" not in decision


def test_chat_bridge_main_guard_blocks_before_docio_selection():
    source = (ROOT / "main.py").read_text(encoding="utf-8-sig")

    guard_at = source.index("has_document_artifact_write_blocker(message)")
    selected_at = source.index("DOCIO0014_CHAT_BRIDGE_SELECTED")

    assert guard_at < selected_at
    assert "DOCIO0018_CHAT_BRIDGE_GOVERNANCE_BLOCKED" in source
    assert has_document_artifact_write_blocker(
        "Modo observe_only e proposal_only. Nao gere artefato. Entregue somente uma proposta textual."
    )


def test_chat_bridge_boot_canary_proves_governance_guard_loaded():
    source = (ROOT / "main.py").read_text(encoding="utf-8-sig")

    assert DOCIO0018_BRIDGE_GOVERNANCE_GUARD_VERSION == "DOCIO0018_BRIDGE_GOVERNANCE_GUARD_V1"
    assert "DOCIO0018_BOOT_GUARD_PRESENT" in source
    assert "blocker_probe=%s" in source
    assert "DOCIO0018_CHAT_BRIDGE_GOVERNANCE_BLOCKED" in source
    assert has_document_artifact_write_blocker(
        "Modo observe_only e proposal_only. Nao escreva arquivo, nao gere artefato."
    )


def test_docio002_format_precedence_boot_canary_present():
    source = (ROOT / "main.py").read_text(encoding="utf-8-sig")

    assert "DOCIO002_FORMAT_PRECEDENCE_BOOT" in source
    assert "expected_format=pptx" in source
    assert "DOCIO002_FORMAT_PRECEDENCE_VERSION" in source


def test_payload_builder_uses_authorized_source_rows_for_three_names():
    message = "por favor, gere uma nova planilha com apenas 3 nomes que vc escolher da planilha anterior"
    decision = classify_document_artifact_request(message, agent_slug="orkio")
    source_context = {
        "file_context_block": "\n".join(
            [
                "DOCUMENTOS ANEXADOS A THREAD - CONTEXTO AUTORIZADO:",
                "[Arquivo: Base de Associados - Amcham RS. 2026.xlsx]",
                "Sheet: 1. BASE DE SOCIOS GERAL CONS...",
                "Cliente | Nome Fantasia | Segmento",
                "A GRINGS S A | PICCADILLY | VAREJO",
                "A PLAYERS PRESTADORA DE SERVICOS EIRELI | A PLAYERS | SERVICOS",
                "ACADEMIA BELEZA DO FUTURO CONSULTORIA E | BELEZA DO FUTURO | SERVICOS",
                "ACADEMICUM AI | ACADEMICUM AI | SERVICOS",
            ]
        )
    }

    plan = build_document_artifact_payload(
        message,
        decision,
        thread_id="thread-a",
        requested_agent_hint="orkio",
        source_context=source_context,
    )

    assert plan["format"] == "xlsx"
    assert plan["rows"] == [
        ["Cliente", "Nome Fantasia", "Segmento"],
        ["A GRINGS S A", "PICCADILLY", "VAREJO"],
        ["A PLAYERS PRESTADORA DE SERVICOS EIRELI", "A PLAYERS", "SERVICOS"],
        ["ACADEMIA BELEZA DO FUTURO CONSULTORIA E", "BELEZA DO FUTURO", "SERVICOS"],
    ]
    assert "Registro de teste A" not in str(plan["rows"])


def test_payload_builder_uses_authorized_source_rows_for_pptx_followup():
    message = "Por favor, agora gere um pptx com as mesmas informacoes"
    decision = classify_document_artifact_request(message, agent_slug="orkio")
    source_context = {
        "citations": [
            {
                "content": "\n".join(
                    [
                        "Cliente | Nome Fantasia | Segmento",
                        "A GRINGS S A | PICCADILLY | VAREJO",
                        "A PLAYERS PRESTADORA DE SERVICOS EIRELI | A PLAYERS | SERVICOS",
                        "ACADEMIA BELEZA DO FUTURO CONSULTORIA E | BELEZA DO FUTURO | SERVICOS",
                    ]
                )
            }
        ]
    }

    plan = build_document_artifact_payload(
        message,
        decision,
        thread_id="thread-a",
        requested_agent_hint="orkio",
        source_context=source_context,
    )

    assert plan["format"] == "pptx"
    assert plan["rows"][0] == ["Cliente", "Nome Fantasia", "Segmento"]
    assert plan["rows"][1][0] == "A GRINGS S A"
    assert "Dados de origem" in plan["content"]


def test_explicit_pptx_format_wins_over_spreadsheet_source_words():
    message = """Orkio, gere um PPTX executivo de teste com base na planilha que enviei anteriormente.

Use apenas 3 empresas da planilha.
A apresentação deve conter:
1. capa;
2. resumo executivo;
3. tabela com as 3 empresas escolhidas;
4. próximos passos recomendados.

Formato: PPTX."""

    decision = classify_document_artifact_request(message, agent_slug="orkio")

    assert decision["handled"] is True
    assert decision["format"] == "pptx"


def test_source_bound_pptx_without_source_rows_refuses_fallback_data():
    message = """Orkio, gere um PPTX executivo de teste com base na planilha que enviei anteriormente.

Use apenas 3 empresas da planilha.
Formato: PPTX."""

    decision = classify_document_artifact_request(message, agent_slug="orkio")

    assert DOCIO003_SOURCE_BINDING_VERSION == "DOCIO003_SOURCE_BINDING_V1"
    assert decision["handled"] is True
    assert decision["format"] == "pptx"
    try:
        build_document_artifact_payload(
            message,
            decision,
            thread_id="thread-a",
            requested_agent_hint="orkio",
            source_context={},
        )
    except ValueError as e:
        assert str(e) == "document_source_rows_required"
    else:
        raise AssertionError("source-bound artifact generation must not use fallback rows")

    assert "Nao gerei o pptx" in source_binding_unavailable_message("pptx")


def test_docio005_real_xlsx_with_attached_file_but_no_rows_refuses_synthetic_fallback():
    message = (
        "Orkio, gere uma nova planilha XLSX com apenas 3 registros reais "
        "da planilha que enviei anteriormente. Formato: XLSX."
    )
    decision = classify_document_artifact_request(message, agent_slug="orkio")

    assert DOCIO005_PREMIUM_SOURCE_CONTRACT_VERSION == "DOCIO005_PREMIUM_SOURCE_CONTRACT_V1"
    assert decision["handled"] is True
    assert decision["format"] == "xlsx"

    try:
        build_document_artifact_payload(
            message,
            decision,
            thread_id="thread-a",
            requested_agent_hint="orkio",
            source_context={"thread_file_ids": ["file-a"], "file_context_block": ""},
        )
    except ValueError as e:
        assert str(e) == "document_source_rows_required"
    else:
        raise AssertionError("real source-bound XLSX must not fall back to synthetic rows")


def test_docio005_docx_can_bind_to_pptx_source_outline():
    message = "Orkio, gere um DOCX executivo com base no PPT que enviei. Formato: DOCX."
    decision = classify_document_artifact_request(message, agent_slug="orkio")
    source_context = {
        "file_context_block": "\n".join(
            [
                "[Arquivo: Inteligencia-Artificial-para-Decisoes-Estrategicas.pptx]",
                "Slide 1",
                "Inteligência Artificial para Decisões Estratégicas",
                "A transformação digital é um desafio crítico.",
                "Slide 2",
                "O Problema",
                "Decisões sem Dados",
                "Baixa Eficiência",
            ]
        )
    }

    plan = build_document_artifact_payload(
        message,
        decision,
        thread_id="thread-a",
        requested_agent_hint="orkio",
        source_context=source_context,
    )

    assert plan["format"] == "docx"
    assert plan["slides"][0]["title"] == "Inteligência Artificial para Decisões Estratégicas"
    assert "O Problema" in plan["content"]
    assert "Registro de teste A" not in str(plan)


def test_source_bound_pptx_with_source_rows_preserves_real_company_names():
    message = """Orkio, gere um PPTX executivo de teste com base na planilha que enviei anteriormente.

Use apenas 3 empresas da planilha.
Formato: PPTX."""
    decision = classify_document_artifact_request(message, agent_slug="orkio")
    source_context = {
        "file_context_block": "\n".join(
            [
                "DOCUMENTOS ANEXADOS A THREAD - CONTEXTO AUTORIZADO:",
                "[Arquivo: Base de Associados - Amcham RS. 2026.xlsx]",
                "Cliente | Nome Fantasia | Segmento",
                "A GRINGS S A | PICCADILLY | VAREJO",
                "A PLAYERS PRESTADORA DE SERVICOS EIRELI | A PLAYERS | SERVICOS",
                "ACADEMIA BELEZA DO FUTURO CONSULTORIA E | BELEZA DO FUTURO | SERVICOS",
            ]
        )
    }

    plan = build_document_artifact_payload(
        message,
        decision,
        thread_id="thread-a",
        requested_agent_hint="orkio",
        source_context=source_context,
    )

    assert plan["format"] == "pptx"
    assert plan["rows"] == [
        ["Cliente", "Nome Fantasia", "Segmento"],
        ["A GRINGS S A", "PICCADILLY", "VAREJO"],
        ["A PLAYERS PRESTADORA DE SERVICOS EIRELI", "A PLAYERS", "SERVICOS"],
        ["ACADEMIA BELEZA DO FUTURO CONSULTORIA E", "BELEZA DO FUTURO", "SERVICOS"],
    ]
    assert "Registro de teste A" not in str(plan["rows"])


def test_source_bound_pptx_uses_source_slide_outline_instead_of_table_fallback():
    message = "Orkio, crie uma apresentacao melhor com base no PPT que enviei. Formato: PPTX."
    decision = classify_document_artifact_request(message, agent_slug="orkio")
    source_context = {
        "file_context_block": "\n".join(
            [
                "DOCUMENTOS ANEXADOS A THREAD - CONTEXTO AUTORIZADO:",
                "[Arquivo: Inteligencia-Artificial-para-Decisoes-Estrategicas.pptx]",
                "Slide 1",
                "Inteligência Artificial para Decisões Estratégicas",
                "A transformação digital é um desafio crítico para PMEs e empresas familiares.",
                "Slide 2",
                "O Problema",
                "Decisões sem Dados",
                "Baixa Eficiência",
                "Dependência do CEO",
                "Slide 3",
                "Solução PATROAI",
                "Agentes para CEOs",
                "Automações Especializadas",
            ]
        )
    }

    plan = build_document_artifact_payload(
        message,
        decision,
        thread_id="thread-a",
        requested_agent_hint="orkio",
        source_context=source_context,
    )

    assert DOCIO004_PPTX_SOURCE_QUALITY_VERSION == "DOCIO004_PPTX_SOURCE_QUALITY_V1"
    assert plan["format"] == "pptx"
    assert plan["slides"][0]["title"] == "Inteligência Artificial para Decisões Estratégicas"
    assert plan["slides"][1]["title"] == "O Problema"
    assert plan["slides"][2]["title"] == "Solução PATROAI"
    assert plan["rows"] is None
    assert "Registro de teste A" not in str(plan)


def test_docio005_boot_canary_present():
    source = (ROOT / "main.py").read_text(encoding="utf-8-sig")
    assert "DOCIO005_PREMIUM_SOURCE_CONTRACT_BOOT" in source
    assert "attached_without_rows_blocked=%s" in source
    assert "DOCIO005_PREMIUM_SOURCE_CONTRACT_VERSION" in source


def test_payload_builder_respects_exact_row_limit_without_visible_header():
    message = "por favor, gere uma nova planilha com apenas 3 nomes que vc escolher da planilha anterior"
    decision = classify_document_artifact_request(message, agent_slug="orkio")
    source_context = {
        "file_context_block": "\n".join(
            [
                "CHOICEST PSICOLOGIA ORGANIZACIONAL EIREL | CHOICEST | SERVICOS",
                "CIA ULTRAGAZ S/A | ULTRAGAZ | SERVICOS",
                "CIX CONSULTING LTDA | CIX CONSULTING | SERVICOS",
                "CLARO S A PORTO ALEGRE | CLARO | SERVICOS",
            ]
        )
    }

    plan = build_document_artifact_payload(
        message,
        decision,
        thread_id="thread-a",
        requested_agent_hint="orkio",
        source_context=source_context,
    )

    assert plan["rows"] == [
        ["CHOICEST PSICOLOGIA ORGANIZACIONAL EIREL", "CHOICEST", "SERVICOS"],
        ["CIA ULTRAGAZ S/A", "ULTRAGAZ", "SERVICOS"],
        ["CIX CONSULTING LTDA", "CIX CONSULTING", "SERVICOS"],
    ]
    assert len(plan["rows"]) == 3
