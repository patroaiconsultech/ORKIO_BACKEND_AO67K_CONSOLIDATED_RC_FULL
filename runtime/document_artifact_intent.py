from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional


SUPPORTED_ARTIFACT_FORMATS = ("md", "csv", "xlsx", "docx", "pptx", "pdf")

_FORMAT_HINTS = (
    ("xlsx", ("planilha", "excel", ".xlsx", " xlsx")),
    ("csv", ("arquivo csv", ".csv", " csv")),
    ("pptx", ("apresentacao", "slides", "slide", "powerpoint", ".pptx", " pptx")),
    ("docx", ("documento word", "arquivo word", "word", ".docx", " docx")),
    ("pdf", ("arquivo pdf", "documento pdf", ".pdf", " pdf")),
    ("md", ("markdown", ".md", " md")),
)

_EXECUTION_VERBS = (
    "gere",
    "gerar",
    "crie",
    "criar",
    "monte",
    "montar",
    "produza",
    "produzir",
    "exporte",
    "exportar",
    "prepare",
    "preparar",
    "construa",
    "construir",
    "faca",
    "fazer",
)

_INSTRUCTIONAL_MARKERS = (
    "como criar",
    "como gerar",
    "como montar",
    "como fazer",
    "me ensine",
    "ensine-me",
    "explique como",
    "guia para",
    "passo a passo",
)

_ARTIFACT_NOUNS = (
    "planilha",
    "excel",
    "csv",
    "documento",
    "arquivo",
    "word",
    "apresentacao",
    "slides",
    "powerpoint",
    "pdf",
    "markdown",
    "relatorio",
)


def _plain(value: Any) -> str:
    raw = str(value or "").strip().lower()
    normalized = unicodedata.normalize("NFKD", raw)
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _display_agent_slug(value: Any) -> str:
    raw = _plain(value).lstrip("@")
    if "orion" in raw or raw == "cto":
        return "orion"
    if "orkio" in raw:
        return "orkio"
    if "chris" in raw:
        return "chris"
    return raw or "orkio"


def _infer_format(low: str) -> Optional[str]:
    for fmt, hints in _FORMAT_HINTS:
        if any(hint in low for hint in hints):
            return fmt
    if any(noun in low for noun in ("documento", "arquivo", "relatorio")):
        return "md"
    return None


def classify_document_artifact_request(
    message: Any,
    *,
    agent_slug: Any = None,
) -> Dict[str, Any]:
    """Classify explicit user requests to create downloadable artifacts.

    The classifier is intentionally conservative. Instructional questions such as
    "como criar uma planilha" stay in conversational mode. Only an explicit
    creation verb plus an artifact noun/format activates the write path.
    """

    raw = str(message or "").strip()
    low = _plain(raw)
    if not raw:
        return {"handled": False, "reason": "empty_message"}

    if any(marker in low for marker in _INSTRUCTIONAL_MARKERS):
        return {"handled": False, "reason": "instructional_request"}

    has_execution_verb = any(
        re.search(rf"\b{re.escape(verb)}\b", low)
        for verb in _EXECUTION_VERBS
    )
    if not has_execution_verb:
        return {"handled": False, "reason": "no_explicit_creation_verb"}

    if not any(noun in low for noun in _ARTIFACT_NOUNS):
        return {"handled": False, "reason": "no_artifact_noun"}

    fmt = _infer_format(low)
    if fmt not in SUPPORTED_ARTIFACT_FORMATS:
        return {"handled": False, "reason": "unsupported_or_unknown_format"}

    owner = _display_agent_slug(agent_slug)
    if owner not in {"orkio", "orion"}:
        return {
            "handled": False,
            "reason": "agent_not_allowed_for_document_generation",
            "agent_slug": owner,
        }

    return {
        "handled": True,
        "capability": "document_artifact_generate",
        "format": fmt,
        "agent_slug": owner,
        "reason": "explicit_document_artifact_request",
        "write_kind": "user_requested_artifact",
        "human_approval_required": False,
    }


def _extract_requested_columns(message: str) -> List[str]:
    low = _plain(message)
    match = re.search(
        r"\bcolunas?\s*(?:\:|=|com|contendo)?\s*(.+)",
        low,
        flags=re.IGNORECASE,
    )
    if not match:
        return []

    tail = match.group(1)
    tail = re.split(r"[.;\n]", tail, maxsplit=1)[0]
    tail = re.sub(r"\bpor favor\b.*$", "", tail).strip()
    pieces = re.split(r"\s*,\s*|\s+e\s+", tail)
    columns: List[str] = []
    for piece in pieces:
        clean = re.sub(r"[^a-z0-9 _/-]+", "", piece, flags=re.IGNORECASE).strip()
        if clean and clean not in columns:
            columns.append(clean[:48].title())
        if len(columns) >= 12:
            break
    return columns


def _spreadsheet_rows(message: str) -> List[List[str]]:
    requested = _extract_requested_columns(message)
    if requested:
        rows = [requested]
        for index in range(1, 4):
            rows.append([f"Exemplo {index}" for _ in requested])
        return rows

    low = _plain(message)
    if any(term in low for term in ("empresa", "empresas", "cliente", "clientes", "contato")):
        return [
            ["Nome da Empresa", "Nome Fantasia", "Segmento", "Localização", "Contato"],
            ["EXEMPLO LTDA", "EXEMPLO", "SERVIÇOS", "São Paulo", "contato@exemplo.com"],
            ["TESTE S/A", "TESTE", "VAREJO", "Rio de Janeiro", "teste@teste.com"],
            ["DEMO TECNOLOGIA LTDA", "DEMO", "TECNOLOGIA", "Porto Alegre", "demo@exemplo.com"],
        ]

    return [
        ["Item", "Descrição", "Status", "Observação"],
        ["1", "Registro de teste A", "Ativo", "Gerado pela ORKIO"],
        ["2", "Registro de teste B", "Em análise", "Exemplo controlado"],
        ["3", "Registro de teste C", "Concluído", "Validação DOCIO"],
    ]


def _title_for_format(fmt: str, message: str) -> str:
    low = _plain(message)
    if "teste" in low:
        return {
            "xlsx": "Planilha de teste",
            "csv": "Dados de teste",
            "docx": "Documento de teste",
            "pptx": "Apresentação de teste",
            "pdf": "Relatório de teste",
            "md": "Documento de teste",
        }[fmt]

    return {
        "xlsx": "Planilha ORKIO",
        "csv": "Dados ORKIO",
        "docx": "Documento ORKIO",
        "pptx": "Apresentação ORKIO",
        "pdf": "Relatório ORKIO",
        "md": "Documento ORKIO",
    }[fmt]


def build_document_artifact_payload(
    message: Any,
    decision: Dict[str, Any],
    *,
    thread_id: Optional[str],
    requested_agent_hint: Optional[str],
) -> Dict[str, Any]:
    """Build a deterministic, bounded payload for the DOCIO generator."""

    raw = str(message or "").strip()
    fmt = str(decision.get("format") or "md").strip().lower()
    if fmt not in SUPPORTED_ARTIFACT_FORMATS:
        raise ValueError(f"unsupported_document_format:{fmt}")

    title = _title_for_format(fmt, raw)
    rows: Optional[List[List[str]]] = None
    if fmt in {"xlsx", "csv"}:
        rows = _spreadsheet_rows(raw)

    content = (
        "Artefato criado a partir de uma solicitação explícita do usuário.\n\n"
        f"Solicitação original: {raw[:4_000]}"
    )
    if fmt in {"docx", "pptx", "pdf", "md"}:
        content += (
            "\n\nConteúdo inicial gerado de forma determinística e auditável. "
            "A edição posterior do conteúdo não altera a evidência da criação original."
        )

    return {
        "format": fmt,
        "title": title,
        "content": content,
        "filename": title,
        "rows": rows,
        "thread_id": str(thread_id or "").strip() or None,
        "requested_agent_hint": str(requested_agent_hint or "").strip() or None,
    }


def artifact_success_message(*, agent_name: str, filename: str) -> str:
    safe_agent = str(agent_name or "Orkio").strip() or "Orkio"
    safe_filename = str(filename or "arquivo").strip() or "arquivo"
    return (
        f"{safe_agent} criou o artefato **{safe_filename}** com sucesso. "
        "Use o botão **Baixar arquivo** no card exibido nesta conversa."
    )
