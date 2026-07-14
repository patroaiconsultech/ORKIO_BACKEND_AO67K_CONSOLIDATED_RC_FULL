from __future__ import annotations

import csv
import io
import multiprocessing as mp
import os
import re
import textwrap
import threading
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional


_ABSOLUTE_MAX_REQUEST_BYTES = 8 * 1024 * 1024
_ABSOLUTE_MAX_ROWS = 2_000
_ABSOLUTE_MAX_COLUMNS = 80
_ABSOLUTE_MAX_CELL_CHARS = 4_000
_ABSOLUTE_MAX_TOTAL_CELLS = 50_000
_ABSOLUTE_MAX_ARTIFACT_BYTES = 10 * 1024 * 1024
_ABSOLUTE_MAX_TIMEOUT_SECONDS = 60.0


class DocumentArtifactError(Exception):
    """Base DOCIO artifact error."""


class DocumentArtifactLimitError(DocumentArtifactError, ValueError):
    """Trusted generation limit was exceeded."""


class DocumentArtifactTimeoutError(DocumentArtifactError, TimeoutError):
    """Isolated generator exceeded its deadline and was terminated."""


class DocumentArtifactWorkerError(DocumentArtifactError, RuntimeError):
    """Isolated generator failed or exited without a valid result."""


class DocumentArtifactConcurrencyError(DocumentArtifactError, RuntimeError):
    """This replica has no free isolated generation slot."""


_GENERATION_STATE_LOCK = threading.Lock()
_GENERATION_ACTIVE = 0


@dataclass(frozen=True)
class DocumentArtifactLimits:
    max_request_bytes: int = 2 * 1024 * 1024
    max_rows: int = 1_000
    max_columns: int = 50
    max_cell_chars: int = 2_000
    max_total_cells: int = 25_000
    max_artifact_bytes: int = 5 * 1024 * 1024
    generation_timeout_seconds: float = 30.0

    @classmethod
    def from_env(cls) -> "DocumentArtifactLimits":
        return cls(
            max_request_bytes=_bounded_int(
                "ORKIO_DOCIO_MAX_REQUEST_BYTES",
                2 * 1024 * 1024,
                minimum=16 * 1024,
                maximum=_ABSOLUTE_MAX_REQUEST_BYTES,
            ),
            max_rows=_bounded_int(
                "ORKIO_DOCIO_MAX_ROWS",
                1_000,
                minimum=1,
                maximum=_ABSOLUTE_MAX_ROWS,
            ),
            max_columns=_bounded_int(
                "ORKIO_DOCIO_MAX_COLUMNS",
                50,
                minimum=1,
                maximum=_ABSOLUTE_MAX_COLUMNS,
            ),
            max_cell_chars=_bounded_int(
                "ORKIO_DOCIO_MAX_CELL_CHARS",
                2_000,
                minimum=1,
                maximum=_ABSOLUTE_MAX_CELL_CHARS,
            ),
            max_total_cells=_bounded_int(
                "ORKIO_DOCIO_MAX_TOTAL_CELLS",
                25_000,
                minimum=1,
                maximum=_ABSOLUTE_MAX_TOTAL_CELLS,
            ),
            max_artifact_bytes=_bounded_int(
                "ORKIO_DOCIO_MAX_ARTIFACT_BYTES",
                5 * 1024 * 1024,
                minimum=1_024,
                maximum=_ABSOLUTE_MAX_ARTIFACT_BYTES,
            ),
            generation_timeout_seconds=_bounded_float(
                "ORKIO_DOCIO_GENERATION_TIMEOUT_SECONDS",
                30.0,
                minimum=0.25,
                maximum=_ABSOLUTE_MAX_TIMEOUT_SECONDS,
            ),
        )


@dataclass
class GeneratedDocumentArtifact:
    filename: str
    content: bytes
    mime_type: str
    text_content: str
    format: str


def _bounded_int(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw = os.getenv(name)
    try:
        value = int(raw) if raw not in (None, "") else int(default)
    except (TypeError, ValueError):
        value = int(default)
    return max(minimum, min(value, maximum))


def _bounded_float(name: str, default: float, *, minimum: float, maximum: float) -> float:
    raw = os.getenv(name)
    try:
        value = float(raw) if raw not in (None, "") else float(default)
    except (TypeError, ValueError):
        value = float(default)
    return max(minimum, min(value, maximum))


def _try_acquire_generation_slot() -> bool:
    global _GENERATION_ACTIVE
    maximum = _bounded_int(
        "ORKIO_DOCIO_MAX_CONCURRENT_GENERATIONS",
        2,
        minimum=1,
        maximum=8,
    )
    with _GENERATION_STATE_LOCK:
        if _GENERATION_ACTIVE >= maximum:
            return False
        _GENERATION_ACTIVE += 1
        return True


def _release_generation_slot() -> None:
    global _GENERATION_ACTIVE
    with _GENERATION_STATE_LOCK:
        _GENERATION_ACTIVE = max(0, _GENERATION_ACTIVE - 1)


def _active_generation_slots() -> int:
    with _GENERATION_STATE_LOCK:
        return int(_GENERATION_ACTIVE)


def _safe_name(value: Any, fallback: str = "orkio_document") -> str:
    raw = _text(value).strip() or fallback
    raw = raw.replace("\r", " ").replace("\n", " ")
    raw = re.sub(r"[^A-Za-z0-9À-ÿ_. -]+", "_", raw)
    raw = re.sub(r"\s+", "_", raw).strip("._- ")
    return raw[:80] or fallback


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\x00", "").strip()


def neutralize_spreadsheet_formula(value: Any) -> str:
    """Keep untrusted spreadsheet content as text.

    Excel-compatible programs may execute cells beginning with =, +, - or @.
    Prefixing with an apostrophe is the portable safe default.
    """

    text = _text(value)
    if text.startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def _normalize_rows(
    rows: Optional[Iterable[Any]],
    limits: DocumentArtifactLimits,
) -> List[List[str]]:
    out: List[List[str]] = []
    total_cells = 0

    if rows is None:
        return out
    if isinstance(rows, (str, bytes, bytearray, Mapping)):
        raise DocumentArtifactLimitError("rows_must_be_an_array")

    for row_index, row in enumerate(rows):
        if row_index >= limits.max_rows:
            raise DocumentArtifactLimitError("max_rows_exceeded")

        if isinstance(row, Mapping):
            raw_values = list(row.values())
        elif isinstance(row, (list, tuple)):
            raw_values = list(row)
        else:
            raw_values = [row]

        if len(raw_values) > limits.max_columns:
            raise DocumentArtifactLimitError("max_columns_exceeded")

        total_cells += len(raw_values)
        if total_cells > limits.max_total_cells:
            raise DocumentArtifactLimitError("max_total_cells_exceeded")

        values: List[str] = []
        for value in raw_values:
            text = _text(value)
            if len(text) > limits.max_cell_chars:
                raise DocumentArtifactLimitError("max_cell_chars_exceeded")
            values.append(text)

        if any(value != "" for value in values):
            out.append(values)

    return out


def _plain_table(rows: List[List[str]]) -> str:
    return "\n".join(
        " | ".join(cell for cell in row)
        for row in rows
        if any(cell != "" for cell in row)
    ).strip()


def _markdown(title: str, body: str, rows: List[List[str]]) -> str:
    parts = [f"# {title}".strip(), "", body.strip()]
    if rows:
        parts.extend(["", "## Dados", "", _plain_table(rows)])
    return "\n".join(part for part in parts if part is not None).strip() + "\n"


def _generate_md(
    title: str,
    body: str,
    rows: List[List[str]],
    basename: str,
) -> GeneratedDocumentArtifact:
    text = _markdown(title, body, rows)
    return GeneratedDocumentArtifact(
        filename=f"{basename}.md",
        content=text.encode("utf-8"),
        mime_type="text/markdown; charset=utf-8",
        text_content=text,
        format="md",
    )


def _generate_csv(
    title: str,
    body: str,
    rows: List[List[str]],
    basename: str,
) -> GeneratedDocumentArtifact:
    out = io.StringIO(newline="")
    writer = csv.writer(out)
    if rows:
        writer.writerows(
            [[neutralize_spreadsheet_formula(value) for value in row] for row in rows]
        )
    else:
        writer.writerow(["title", "content"])
        writer.writerow(
            [
                neutralize_spreadsheet_formula(title),
                neutralize_spreadsheet_formula(body),
            ]
        )
    text = out.getvalue()
    return GeneratedDocumentArtifact(
        filename=f"{basename}.csv",
        content=text.encode("utf-8-sig"),
        mime_type="text/csv; charset=utf-8",
        text_content=text,
        format="csv",
    )


def _generate_xlsx(
    title: str,
    body: str,
    rows: List[List[str]],
    basename: str,
) -> GeneratedDocumentArtifact:
    try:
        from openpyxl import Workbook  # type: ignore
    except Exception as exc:
        raise RuntimeError("openpyxl_unavailable") from exc

    wb = Workbook()
    ws = wb.active
    ws.title = "Orkio"
    ws.append([neutralize_spreadsheet_formula(title)])
    if body:
        ws.append([neutralize_spreadsheet_formula(body)])
    if rows:
        ws.append([])
        for row in rows:
            ws.append([neutralize_spreadsheet_formula(value) for value in row])

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


def _generate_docx(
    title: str,
    body: str,
    rows: List[List[str]],
    basename: str,
) -> GeneratedDocumentArtifact:
    try:
        from docx import Document  # type: ignore
    except Exception as exc:
        raise RuntimeError("python_docx_unavailable") from exc

    doc = Document()
    doc.add_heading(title, level=1)
    for paragraph in [part.strip() for part in body.splitlines() if part.strip()]:
        doc.add_paragraph(paragraph)
    if rows:
        width = max(len(row) for row in rows)
        table = doc.add_table(rows=0, cols=width)
        for row in rows:
            cells = table.add_row().cells
            for index, value in enumerate(row):
                cells[index].text = value

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


def _generate_pptx(
    title: str,
    body: str,
    rows: List[List[str]],
    basename: str,
) -> GeneratedDocumentArtifact:
    try:
        from pptx import Presentation  # type: ignore
        from pptx.util import Inches  # type: ignore
    except Exception as exc:
        raise RuntimeError("python_pptx_unavailable") from exc

    deck = Presentation()
    title_slide = deck.slides.add_slide(deck.slide_layouts[0])
    title_slide.shapes.title.text = title
    subtitle = title_slide.placeholders[1] if len(title_slide.placeholders) > 1 else None
    if subtitle is not None:
        subtitle.text = body[:2_000]

    if rows:
        slide = deck.slides.add_slide(deck.slide_layouts[5])
        slide.shapes.title.text = "Dados"
        table = slide.shapes.add_table(
            len(rows),
            max(len(row) for row in rows),
            Inches(0.7),
            Inches(1.4),
            Inches(8.6),
            Inches(4.8),
        ).table
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                table.cell(row_index, column_index).text = value

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


def _generate_pdf(
    title: str,
    body: str,
    rows: List[List[str]],
    basename: str,
) -> GeneratedDocumentArtifact:
    try:
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore
        from reportlab.pdfbase.pdfmetrics import stringWidth  # type: ignore
    except Exception as exc:
        raise RuntimeError("reportlab_unavailable") from exc

    stream = io.BytesIO()
    pdf = canvas.Canvas(stream, pagesize=A4)
    width, height = A4
    left = 72
    right = width - 72
    y = height - 72

    def draw_wrapped(value: str, *, font: str, size: int, leading: int) -> None:
        nonlocal y
        pdf.setFont(font, size)
        max_width = max(80, right - left)
        for source_line in (value or "").splitlines() or [""]:
            words = source_line.split()
            if not words:
                y -= leading
                continue
            current = ""
            for word in words:
                candidate = word if not current else f"{current} {word}"
                if stringWidth(candidate, font, size) <= max_width:
                    current = candidate
                    continue
                if y < 72:
                    pdf.showPage()
                    y = height - 72
                    pdf.setFont(font, size)
                pdf.drawString(left, y, current)
                y -= leading
                current = word
            if current:
                if y < 72:
                    pdf.showPage()
                    y = height - 72
                    pdf.setFont(font, size)
                pdf.drawString(left, y, current)
                y -= leading

    draw_wrapped(title, font="Helvetica-Bold", size=16, leading=22)
    y -= 6
    draw_wrapped(body, font="Helvetica", size=10, leading=15)
    if rows:
        y -= 6
        draw_wrapped(_plain_table(rows), font="Helvetica", size=9, leading=13)
    pdf.save()

    text = _markdown(title, body, rows)
    return GeneratedDocumentArtifact(
        filename=f"{basename}.pdf",
        content=stream.getvalue(),
        mime_type="application/pdf",
        text_content=text,
        format="pdf",
    )


def generate_document_artifact(
    payload: Dict[str, Any],
    *,
    limits: Optional[DocumentArtifactLimits] = None,
) -> GeneratedDocumentArtifact:
    trusted = limits or DocumentArtifactLimits.from_env()
    fmt = _text(payload.get("format") or payload.get("file_format") or "md").lower().lstrip(".")
    aliases = {
        "markdown": "md",
        "excel": "xlsx",
        "word": "docx",
        "powerpoint": "pptx",
    }
    fmt = aliases.get(fmt, fmt)

    title = _text(payload.get("title")) or "Documento Orkio"
    body = _text(payload.get("content") or payload.get("body") or payload.get("markdown"))
    rows = _normalize_rows(payload.get("rows") or payload.get("table_rows"), trusted)
    basename = _safe_name(payload.get("filename") or title)

    if len(title) > 180:
        raise DocumentArtifactLimitError("title_too_long")
    if len(body) > 200_000:
        raise DocumentArtifactLimitError("content_too_long")

    generators = {
        "md": _generate_md,
        "csv": _generate_csv,
        "xlsx": _generate_xlsx,
        "docx": _generate_docx,
        "pptx": _generate_pptx,
        "pdf": _generate_pdf,
    }
    generator = generators.get(fmt)
    if generator is None:
        raise ValueError(f"unsupported_document_format:{fmt}")

    artifact = generator(title, body, rows, basename)
    if len(artifact.content) > trusted.max_artifact_bytes:
        raise DocumentArtifactLimitError("max_artifact_bytes_exceeded")
    return artifact


def _artifact_worker(
    payload: Dict[str, Any],
    limits_payload: Dict[str, Any],
    sender: Any,
) -> None:
    try:
        artifact = generate_document_artifact(
            payload,
            limits=DocumentArtifactLimits(**limits_payload),
        )
        sender.send(
            {
                "ok": True,
                "artifact": {
                    "filename": artifact.filename,
                    "content": artifact.content,
                    "mime_type": artifact.mime_type,
                    "text_content": artifact.text_content,
                    "format": artifact.format,
                },
            }
        )
    except BaseException as exc:  # child boundary must report all failures
        try:
            sender.send(
                {
                    "ok": False,
                    "error_type": exc.__class__.__name__,
                    "error": str(exc)[:500],
                }
            )
        except Exception:
            pass
    finally:
        try:
            sender.close()
        except Exception:
            pass


def _terminate_process(process: mp.Process) -> None:
    if process.is_alive():
        process.terminate()
        process.join(timeout=2.0)
    if process.is_alive() and hasattr(process, "kill"):
        process.kill()
        process.join(timeout=2.0)
    if process.is_alive():
        raise DocumentArtifactWorkerError("generation_worker_could_not_be_terminated")


def generate_document_artifact_isolated(
    payload: Dict[str, Any],
    *,
    limits: Optional[DocumentArtifactLimits] = None,
    timeout_seconds: Optional[float] = None,
) -> GeneratedDocumentArtifact:
    """Generate in a terminable process guarded by a per-replica hard slot.

    A timeout always terminates and joins the worker before this function returns.
    The concurrency slot is released only after the worker is confirmed stopped,
    so a timed-out process cannot silently escape the resource boundary.
    """

    if not _try_acquire_generation_slot():
        raise DocumentArtifactConcurrencyError(
            "document_generation_concurrency_limit_reached"
        )

    trusted = limits or DocumentArtifactLimits.from_env()
    timeout = (
        trusted.generation_timeout_seconds
        if timeout_seconds is None
        else max(0.05, min(float(timeout_seconds), _ABSOLUTE_MAX_TIMEOUT_SECONDS))
    )

    preferred_method = os.getenv(
        "ORKIO_DOCIO_PROCESS_START_METHOD",
        "spawn",
    ).strip().lower()
    if preferred_method not in {"spawn", "fork", "forkserver"}:
        preferred_method = "spawn"
    if preferred_method not in mp.get_all_start_methods():
        preferred_method = "spawn"

    process: Optional[mp.Process] = None
    receiver = None
    sender = None
    try:
        context = mp.get_context(preferred_method)
        receiver, sender = context.Pipe(duplex=False)
        process = context.Process(
            target=_artifact_worker,
            args=(dict(payload), asdict(trusted), sender),
            daemon=True,
            name="orkio-docio-generator",
        )
        process.start()
        sender.close()
        sender = None

        if not receiver.poll(timeout):
            _terminate_process(process)
            raise DocumentArtifactTimeoutError("document_generation_timeout")

        result = receiver.recv()
        process.join(timeout=2.0)
        if process.is_alive():
            _terminate_process(process)
            raise DocumentArtifactWorkerError("generation_worker_did_not_exit")

        if not isinstance(result, dict) or not result.get("ok"):
            error_type = str((result or {}).get("error_type") or "WorkerError")
            error = str((result or {}).get("error") or "document_generation_failed")
            if error_type == "DocumentArtifactLimitError":
                raise DocumentArtifactLimitError(error)
            if error_type in {"ValueError"}:
                raise ValueError(error)
            if error_type in {"RuntimeError"}:
                raise DocumentArtifactWorkerError(error)
            raise DocumentArtifactWorkerError(f"{error_type}:{error}")

        artifact = result.get("artifact") or {}
        return GeneratedDocumentArtifact(
            filename=str(artifact["filename"]),
            content=bytes(artifact["content"]),
            mime_type=str(artifact["mime_type"]),
            text_content=str(artifact["text_content"]),
            format=str(artifact["format"]),
        )
    except EOFError as exc:
        if process is not None:
            _terminate_process(process)
        raise DocumentArtifactWorkerError(
            "generation_worker_exited_without_result"
        ) from exc
    finally:
        if receiver is not None:
            try:
                receiver.close()
            except Exception:
                pass
        if sender is not None:
            try:
                sender.close()
            except Exception:
                pass
        if process is not None and process.is_alive():
            _terminate_process(process)
        _release_generation_slot()
