import pytest

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
    pytest.importorskip("openpyxl")

    artifact = generate_document_artifact({
        "format": "xlsx",
        "title": "Base",
        "rows": [["Associado", "Segmento"], ["ACME", "Tecnologia"]],
    })

    assert artifact.filename.endswith(".xlsx")
    assert artifact.content.startswith(b"PK")
    assert "ACME" in artifact.text_content
