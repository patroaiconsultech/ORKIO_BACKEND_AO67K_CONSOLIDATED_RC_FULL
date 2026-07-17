import pytest

from runtime.document_artifact_intent import DOCIO006_PREMIUM_ARTIFACT_QUALITY_VERSION
from services.document_artifact_service import generate_document_artifact


def test_generate_markdown_artifact():
    artifact = generate_document_artifact({
        "format": "md",
        "title": "Plano AMCHAM",
        "content": "Diagnostico executivo.",
        "rows": [["Associado", "Segmento"], ["ACME", "Tecnologia"]],
    })

    assert artifact.filename.endswith(".md")
    assert artifact.mime_type.startswith("text/markdown")
    assert b"Plano AMCHAM" in artifact.content
    assert "ACME" in artifact.text_content


def test_generate_csv_artifact():
    artifact = generate_document_artifact({
        "format": "csv",
        "title": "Base",
        "rows": [["Associado", "Segmento"], ["ACME", "Tecnologia"]],
    })

    assert artifact.filename.endswith(".csv")
    assert artifact.mime_type.startswith("text/csv")
    assert "ACME" in artifact.content.decode("utf-8-sig")


def test_generate_xlsx_artifact_when_openpyxl_available():
    openpyxl = pytest.importorskip("openpyxl")

    artifact = generate_document_artifact({
        "format": "xlsx",
        "title": "Base",
        "rows": [["Associado", "Segmento"], ["ACME", "Tecnologia"]],
    })

    assert artifact.filename.endswith(".xlsx")
    assert artifact.content.startswith(b"PK")
    assert "ACME" in artifact.text_content

    workbook = openpyxl.load_workbook(__import__("io").BytesIO(artifact.content))
    assert workbook.sheetnames == ["Dados", "Metadados"]
    assert workbook["Dados"]["A1"].value == "Associado"
    assert workbook["Dados"]["A1"].font.bold is True
    assert workbook["Metadados"]["A1"].value == "Campo"
    assert workbook["Metadados"]["B4"].value == "2"


def test_generate_pptx_artifact_uses_executive_template_when_available():
    pptx = pytest.importorskip("pptx")

    artifact = generate_document_artifact({
        "format": "pptx",
        "title": "Apresentacao AMCHAM",
        "content": "Dados de origem: linhas extraidas do contexto autorizado.",
        "rows": [
            ["Cliente", "Nome Fantasia", "Segmento"],
            ["A GRINGS S A", "PICCADILLY", "VAREJO"],
            ["A PLAYERS PRESTADORA DE SERVICOS EIRELI", "A PLAYERS", "SERVICOS"],
            ["ACADEMIA BELEZA DO FUTURO CONSULTORIA E", "BELEZA DO FUTURO", "SERVICOS"],
        ],
    })

    deck = pptx.Presentation(__import__("io").BytesIO(artifact.content))
    slide_text = "\n".join(
        shape.text
        for slide in deck.slides
        for shape in slide.shapes
        if hasattr(shape, "text")
    )

    assert artifact.filename.endswith(".pptx")
    assert len(deck.slides) >= 4
    assert deck.slide_width > deck.slide_height
    assert "ORKIO" in slide_text
    assert "Resumo executivo" in slide_text
    assert "Dados selecionados" in slide_text
    assert "PICCADILLY" in slide_text
    assert "Proximos passos" in slide_text


def test_generate_pptx_artifact_from_source_slides_preserves_titles():
    pptx = pytest.importorskip("pptx")

    artifact = generate_document_artifact({
        "format": "pptx",
        "title": "Inteligencia Artificial para Decisoes Estrategicas",
        "content": "Dados de origem: estrutura de slides extraida do PPTX autorizado.",
        "slides": [
            {
                "source_slide": 1,
                "title": "Inteligência Artificial para Decisões Estratégicas",
                "bullets": [
                    "A transformação digital é um desafio crítico para PMEs e empresas familiares.",
                ],
            },
            {
                "source_slide": 2,
                "title": "O Problema",
                "bullets": [
                    "Decisões sem Dados",
                    "Baixa Eficiência",
                    "Dependência do CEO",
                ],
            },
            {
                "source_slide": 3,
                "title": "Solução PATROAI",
                "bullets": [
                    "Agentes para CEOs",
                    "Automações Especializadas",
                ],
            },
        ],
    })

    deck = pptx.Presentation(__import__("io").BytesIO(artifact.content))
    slide_text = "\n".join(
        shape.text
        for slide in deck.slides
        for shape in slide.shapes
        if hasattr(shape, "text")
    )

    assert artifact.filename.endswith(".pptx")
    assert DOCIO006_PREMIUM_ARTIFACT_QUALITY_VERSION == "DOCIO006_PREMIUM_ARTIFACT_QUALITY_V1"
    assert deck.slide_width > deck.slide_height
    assert len(deck.slides) >= 6
    assert "Slide fonte 1" in slide_text
    assert "ORKIO" in slide_text
    assert "Inteligência Artificial para Decisões Estratégicas" in slide_text
    assert "O Problema" in slide_text
    assert "Solução PATROAI" in slide_text
    assert "Registro de teste A" not in slide_text


def test_generate_docx_artifact_has_sections_when_available():
    docx = pytest.importorskip("docx")

    artifact = generate_document_artifact({
        "format": "docx",
        "title": "Documento executivo",
        "content": "Analise gerada a partir do contexto autorizado.",
        "rows": [["Cliente", "Segmento"], ["ACME", "Tecnologia"]],
    })

    document = docx.Document(__import__("io").BytesIO(artifact.content))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    footer_text = "\n".join(
        paragraph.text
        for section in document.sections
        for paragraph in section.footer.paragraphs
    )

    assert artifact.filename.endswith(".docx")
    assert "Resumo executivo" in text
    assert "Fonte e governanca" in text
    assert "Proximos passos" in text
    assert "ORKIO" in footer_text


def test_generate_pdf_artifact_has_executive_governance_header_when_available():
    reportlab = pytest.importorskip("reportlab")

    artifact = generate_document_artifact({
        "format": "pdf",
        "title": "Relatorio executivo",
        "content": "Analise gerada a partir do contexto autorizado.",
        "rows": [["Cliente", "Segmento"], ["ACME", "Tecnologia"]],
    })

    assert reportlab is not None
    assert artifact.filename.endswith(".pdf")
    assert artifact.content.startswith(b"%PDF")
    assert b"ORKIO" in artifact.content
    assert "ACME" in artifact.text_content
