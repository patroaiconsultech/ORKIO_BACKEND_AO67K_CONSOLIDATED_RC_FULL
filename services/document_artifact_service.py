from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class GeneratedDocumentArtifact:
    filename: str
    content: bytes
    mime_type: str
    text_content: str
    format: str


def _safe_name(value: Any, fallback: str = "orkio_document") -> str:
    raw = str(value or "").strip() or fallback
    raw = re.sub(r"[^A-Za-z0-9_. -]+", "_", raw)
    raw = re.sub(r"\s+", "_", raw).strip("._- ")
    return raw[:80] or fallback


def _text(value: Any) -> str:
    return str(value or "").replace("\x00", "").strip()


def _rows(rows: Optional[Iterable[Any]]) -> List[List[str]]:
    out: List[List[str]] = []
    for row in list(rows or []):
        if isinstance(row, dict):
            values = [str(v or "").strip() for v in row.values()]
        elif isinstance(row, (list, tuple)):
            values = [str(v or "").strip() for v in row]
        else:
            values = [str(row or "").strip()]
        if any(values):
            out.append(values)
    return out


def _plain_table(rows: List[List[str]]) -> str:
    return "\n".join(" | ".join(cell for cell in row if cell) for row in rows if any(row)).strip()


def _markdown(title: str, body: str, rows: List[List[str]]) -> str:
    parts = [f"# {title}".strip(), "", body.strip()]
    if rows:
        parts.extend(["", "## Dados", "", _plain_table(rows)])
    return "\n".join(part for part in parts if part is not None).strip() + "\n"


def _generate_md(title: str, body: str, rows: List[List[str]], basename: str) -> GeneratedDocumentArtifact:
    text = _markdown(title, body, rows)
    return GeneratedDocumentArtifact(
        filename=f"{basename}.md",
        content=text.encode("utf-8"),
        mime_type="text/markdown; charset=utf-8",
        text_content=text,
        format="md",
    )


def _generate_csv(title: str, body: str, rows: List[List[str]], basename: str) -> GeneratedDocumentArtifact:
    out = io.StringIO()
    writer = csv.writer(out)
    if rows:
        writer.writerows(rows)
    else:
        writer.writerow(["title", "content"])
        writer.writerow([title, body])
    text = out.getvalue()
    return GeneratedDocumentArtifact(
        filename=f"{basename}.csv",
        content=text.encode("utf-8-sig"),
        mime_type="text/csv; charset=utf-8",
        text_content=text,
        format="csv",
    )


def _generate_xlsx(title: str, body: str, rows: List[List[str]], basename: str) -> GeneratedDocumentArtifact:
    try:
        from openpyxl import Workbook  # type: ignore
    except Exception as exc:
        raise RuntimeError("openpyxl_unavailable") from exc

    wb = Workbook()
    ws = wb.active
    ws.title = "Orkio"
    ws.append([title])
    if body:
        ws.append([body])
    if rows:
        ws.append([])
        for row in rows:
            ws.append(row)
    stream = io.BytesIO()
    wb.save(stream)
    text = _markdown(title, body, rows)
    return GeneratedDocumentArtifact(
        filename=f"{basename}.xlsx",
        content=stream.getvalue(),
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        text_content=text,
        format="xlsx",
    )


def _generate_docx(title: str, body: str, rows: List[List[str]], basename: str) -> GeneratedDocumentArtifact:
    try:
        from docx import Document  # type: ignore
    except Exception as exc:
        raise RuntimeError("python_docx_unavailable") from exc

    doc = Document()
    doc.add_heading(title, level=1)
    for paragraph in [p.strip() for p in body.splitlines() if p.strip()]:
        doc.add_paragraph(paragraph)
    if rows:
        width = max(len(row) for row in rows)
        table = doc.add_table(rows=0, cols=width)
        for row in rows:
            cells = table.add_row().cells
            for idx, value in enumerate(row):
                cells[idx].text = value
    stream = io.BytesIO()
    doc.save(stream)
    text = _markdown(title, body, rows)
    return GeneratedDocumentArtifact(
        filename=f"{basename}.docx",
        content=stream.getvalue(),
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        text_content=text,
        format="docx",
    )


def _generate_pptx(title: str, body: str, rows: List[List[str]], basename: str) -> GeneratedDocumentArtifact:
    try:
        from pptx import Presentation  # type: ignore
    except Exception as exc:
        raise RuntimeError("python_pptx_unavailable") from exc

    deck = Presentation()
    title_slide = deck.slides.add_slide(deck.slide_layouts[0])
    title_slide.shapes.title.text = title
    subtitle = title_slide.placeholders[1] if len(title_slide.placeholders) > 1 else None
    if subtitle is not None:
        subtitle.text = body[:500]

    if rows:
        slide = deck.slides.add_slide(deck.slide_layouts[5])
        slide.shapes.title.text = "Dados"
        left = top = width = height = None
        try:
            from pptx.util import Inches  # type: ignore
            left, top, width, height = Inches(0.7), Inches(1.4), Inches(8.6), Inches(4.8)
        except Exception:
            pass
        if left is not None:
            table = slide.shapes.add_table(len(rows), max(len(r) for r in rows), left, top, width, height).table
            for r_idx, row in enumerate(rows):
                for c_idx, value in enumerate(row):
                    table.cell(r_idx, c_idx).text = value

    stream = io.BytesIO()
    deck.save(stream)
    text = _markdown(title, body, rows)
    return GeneratedDocumentArtifact(
        filename=f"{basename}.pptx",
        content=stream.getvalue(),
        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        text_content=text,
        format="pptx",
    )


def _generate_pdf(title: str, body: str, rows: List[List[str]], basename: str) -> GeneratedDocumentArtifact:
    try:
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore
    except Exception as exc:
        raise RuntimeError("reportlab_unavailable") from exc

    stream = io.BytesIO()
    c = canvas.Canvas(stream, pagesize=A4)
    width, height = A4
    y = height - 72
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, title[:90])
    y -= 28
    c.setFont("Helvetica", 10)
    for line in (body.splitlines() + [""] + _plain_table(rows).splitlines()):
        if y < 72:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 72
        c.drawString(72, y, line[:120])
        y -= 15
    c.save()
    text = _markdown(title, body, rows)
    return GeneratedDocumentArtifact(
        filename=f"{basename}.pdf",
        content=stream.getvalue(),
        mime_type="application/pdf",
        text_content=text,
        format="pdf",
    )


def generate_document_artifact(payload: Dict[str, Any]) -> GeneratedDocumentArtifact:
    fmt = str(payload.get("format") or payload.get("file_format") or "md").strip().lower().lstrip(".")
    title = _text(payload.get("title")) or "Documento Orkio"
    body = _text(payload.get("content") or payload.get("body") or payload.get("markdown"))
    rows = _rows(payload.get("rows") or payload.get("table_rows"))
    basename = _safe_name(payload.get("filename") or title)

    if fmt in {"md", "markdown"}:
        return _generate_md(title, body, rows, basename)
    if fmt == "csv":
        return _generate_csv(title, body, rows, basename)
    if fmt in {"xlsx", "excel"}:
        return _generate_xlsx(title, body, rows, basename)
    if fmt in {"docx", "word"}:
        return _generate_docx(title, body, rows, basename)
    if fmt in {"pptx", "powerpoint"}:
        return _generate_pptx(title, body, rows, basename)
    if fmt == "pdf":
        return _generate_pdf(title, body, rows, basename)
    raise ValueError(f"unsupported_document_format:{fmt}")
