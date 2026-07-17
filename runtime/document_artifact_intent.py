from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional


SUPPORTED_ARTIFACT_FORMATS = ("md", "csv", "xlsx", "docx", "pptx", "pdf")
DOCIO0018_BRIDGE_GOVERNANCE_GUARD_VERSION = "DOCIO0018_BRIDGE_GOVERNANCE_GUARD_V1"
DOCIO002_FORMAT_PRECEDENCE_VERSION = "DOCIO002_FORMAT_PRECEDENCE_V1"
DOCIO003_SOURCE_BINDING_VERSION = "DOCIO003_SOURCE_BINDING_V1"
DOCIO004_PPTX_SOURCE_QUALITY_VERSION = "DOCIO004_PPTX_SOURCE_QUALITY_V1"
DOCIO005_PREMIUM_SOURCE_CONTRACT_VERSION = "DOCIO005_PREMIUM_SOURCE_CONTRACT_V1"
DOCIO006_PREMIUM_ARTIFACT_QUALITY_VERSION = "DOCIO006_PREMIUM_ARTIFACT_QUALITY_V1"

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

_GOVERNANCE_WRITE_BLOCKERS = (
    "observe_only",
    "observe only",
    "proposal_only",
    "proposal only",
    "somente proposta",
    "apenas proposta",
    "somente uma proposta textual",
    "apenas uma proposta textual",
    "entregue somente uma proposta textual",
    "entregue apenas uma proposta textual",
    "nao escreva",
    "nao escrever",
    "sem escrita",
    "write_executed=false",
    "write executed false",
    "nao gere artefato",
    "nao gerar artefato",
    "nao crie artefato",
    "nao criar artefato",
    "sem artefato",
    "nao gere arquivo",
    "nao gerar arquivo",
    "nao crie arquivo",
    "nao criar arquivo",
    "sem arquivo",
    "nao crie branch",
    "nao criar branch",
    "sem branch",
    "nao faca commit",
    "nao fazer commit",
    "nao crie commit",
    "nao criar commit",
    "sem commit",
    "nao faca deploy",
    "nao fazer deploy",
    "nao execute deploy",
    "nao executar deploy",
    "sem deploy",
)

_ARTIFACT_NOUNS = (
    "planilha",
    "excel",
    "xlsx",
    "csv",
    "documento",
    "arquivo",
    "word",
    "docx",
    "apresentacao",
    "slides",
    "powerpoint",
    "pptx",
    "pdf",
    "markdown",
    "md",
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
    explicit = re.search(
        r"\b(?:formato|em|como|arquivo)\s*(?:\:|=|de|do|da)?\s*"
        r"(pptx|powerpoint|slides?|xlsx|excel|csv|docx|word|pdf|md|markdown)\b",
        low,
        flags=re.IGNORECASE,
    )
    if explicit:
        token = explicit.group(1).lower()
        aliases = {
            "powerpoint": "pptx",
            "slide": "pptx",
            "slides": "pptx",
            "excel": "xlsx",
            "word": "docx",
            "markdown": "md",
        }
        return aliases.get(token, token)

    extension_hits = re.findall(r"\.(pptx|xlsx|csv|docx|pdf|md)\b", low, flags=re.IGNORECASE)
    if extension_hits:
        return extension_hits[-1].lower()

    for fmt, hints in _FORMAT_HINTS:
        if any(hint in low for hint in hints):
            return fmt
    if any(noun in low for noun in ("documento", "arquivo", "relatorio")):
        return "md"
    return None


def _has_governance_write_blocker(low: str) -> bool:
    return any(marker in low for marker in _GOVERNANCE_WRITE_BLOCKERS)


def has_document_artifact_write_blocker(message: Any) -> bool:
    return _has_governance_write_blocker(_plain(message))


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

    if _has_governance_write_blocker(low):
        return {
            "handled": False,
            "reason": "governance_write_blocked",
            "write_executed": False,
            "artifact_created": False,
            "proposal_only": ("proposal_only" in low or "proposal only" in low),
            "observe_only": ("observe_only" in low or "observe only" in low),
        }

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


def _requires_bound_source_rows(message: str) -> bool:
    low = _plain(message)
    markers = (
        "planilha anterior",
        "arquivo anterior",
        "documento anterior",
        "anexo anterior",
        "planilha enviada",
        "arquivo enviado",
        "documento enviado",
        "anexo enviado",
        "planilha que enviei",
        "arquivo que enviei",
        "documento que enviei",
        "anexo que enviei",
        "planilha que subi",
        "arquivo que subi",
        "com base na planilha",
        "com base no arquivo",
        "com base no documento",
        "baseado na planilha",
        "baseado no arquivo",
        "mesmas informacoes",
        "mesmos dados",
        "da planilha",
        "do arquivo",
    )
    return any(marker in low for marker in markers)


def _requires_bound_source_content(message: str) -> bool:
    low = _plain(message)
    markers = (
        "registro real",
        "registros reais",
        "dado real",
        "dados reais",
        "fonte real",
        "conteudo real",
        "conteudo do arquivo",
        "conteudo da planilha",
        "conteudo do ppt",
        "conteudo do pptx",
        "preserve a tese",
        "preservar a tese",
        "preserve os problemas",
        "preserve a solucao",
        "preserve a soluÃ§Ã£o",
        "preserve os diferenciais",
        "ppt anterior",
        "pptx anterior",
        "powerpoint anterior",
        "apresentacao anterior",
        "apresentação anterior",
        "ppt enviado",
        "pptx enviado",
        "powerpoint enviado",
        "apresentacao enviada",
        "apresentação enviada",
        "ppt que enviei",
        "pptx que enviei",
        "powerpoint que enviei",
        "apresentacao que enviei",
        "apresentação que enviei",
        "ppt que subi",
        "pptx que subi",
        "com base no ppt",
        "com base no pptx",
        "com base no powerpoint",
        "com base na apresentacao",
        "com base na apresentação",
        "a partir do ppt",
        "a partir do pptx",
        "a partir da apresentacao",
        "a partir da apresentação",
    )
    return _requires_bound_source_rows(message) or any(marker in low for marker in markers)


def _source_context_has_attachment_signal(source_context: Any) -> bool:
    if not isinstance(source_context, dict):
        return bool(_source_context_text(source_context))
    for key in (
        "file_ids",
        "thread_file_ids",
        "files_used",
        "citations",
    ):
        value = source_context.get(key)
        if isinstance(value, list) and value:
            return True
    if source_context.get("preferred_file_id"):
        return True
    diagnostic = source_context.get("diagnostic")
    if isinstance(diagnostic, dict):
        try:
            if int(diagnostic.get("file_count") or 0) > 0:
                return True
            if int(diagnostic.get("thread_file_count") or 0) > 0:
                return True
        except Exception:
            pass
    return bool(_source_context_text(source_context))


def _source_slide_summary_text(slides: List[Dict[str, Any]]) -> str:
    if not slides:
        return ""
    parts: List[str] = []
    for slide in slides[:12]:
        title = str(slide.get("title") or "Slide").strip()
        parts.append(title)
        for bullet in list(slide.get("bullets") or [])[:8]:
            clean = str(bullet or "").strip()
            if clean:
                parts.append(f"- {clean}")
    return "\n".join(parts).strip()


def source_binding_unavailable_message(fmt: str) -> str:
    requested = str(fmt or "arquivo").strip().lower() or "arquivo"
    return (
        f"Nao gerei o {requested}, porque o pedido exige dados reais de uma "
        "planilha/arquivo anterior e nao consegui vincular linhas tabulares "
        "autorizadas a esta conversa. Para evitar dados incorretos, reenvie o "
        "arquivo nesta thread ou peca explicitamente um artefato de teste com "
        "dados ficticios."
    )


def _clean_source_line(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if not text:
        return ""
    low = _plain(text)
    if low.startswith("documentos anexados"):
        return ""
    if low.startswith("instrucoes:") or low.startswith("instruções:"):
        return ""
    if low.startswith("fonte tecnica:") or low.startswith("fonte técnica:"):
        return ""
    if text.startswith("[") and text.endswith("]"):
        return ""
    if text in {"'", ".", '"'}:
        return ""
    return text[:220]


def _slides_from_source_context(
    source_context: Any,
    *,
    max_slides: int = 10,
    max_bullets: int = 8,
) -> List[Dict[str, Any]]:
    text = _source_context_text(source_context)
    if not text or not re.search(r"(?im)^\s*slide\s+\d+\b", text):
        return []

    chunks = re.split(r"(?im)^\s*slide\s+(\d+)\s*$", text)
    slides: List[Dict[str, Any]] = []
    for index in range(1, len(chunks), 2):
        number = chunks[index]
        body = chunks[index + 1] if index + 1 < len(chunks) else ""
        lines = [_clean_source_line(line) for line in body.splitlines()]
        lines = [line for line in lines if line]
        if not lines:
            continue

        title = lines[0]
        bullets: List[str] = []
        pending_number = ""
        for line in lines[1:]:
            if re.fullmatch(r"\d{1,2}", line):
                pending_number = line
                continue
            clean = f"{pending_number}. {line}" if pending_number else line
            pending_number = ""
            if clean not in bullets:
                bullets.append(clean)
            if len(bullets) >= max_bullets:
                break

        slides.append(
            {
                "source_slide": int(number) if str(number).isdigit() else len(slides) + 1,
                "title": title,
                "bullets": bullets,
            }
        )
        if len(slides) >= max_slides:
            break
    return slides


def _source_context_text(source_context: Any) -> str:
    if not source_context:
        return ""
    if isinstance(source_context, dict):
        pieces: List[str] = []
        for key in ("file_context_block", "context_block", "content", "text", "excerpt"):
            value = source_context.get(key)
            if value:
                pieces.append(str(value))
        citations = source_context.get("citations")
        if isinstance(citations, list):
            for item in citations[:8]:
                if not isinstance(item, dict):
                    continue
                for key in ("content", "text", "excerpt", "chunk_text", "summary"):
                    value = item.get(key)
                    if value:
                        pieces.append(str(value))
                        break
        return "\n".join(pieces)
    return str(source_context)


def _requested_row_limit(message: str) -> Optional[int]:
    low = _plain(message)
    number_words = {
        "um": 1,
        "uma": 1,
        "dois": 2,
        "duas": 2,
        "tres": 3,
        "quatro": 4,
        "cinco": 5,
        "seis": 6,
        "sete": 7,
        "oito": 8,
        "nove": 9,
        "dez": 10,
    }
    match = re.search(
        r"\b(?:apenas|somente|so|s[oÃ³]|com)?\s*(\d{1,2})\s+"
        r"(?:nomes?|registros?|linhas?|itens?|empresas?|clientes?)\b",
        low,
    )
    if match:
        try:
            return max(1, min(int(match.group(1)), 25))
        except Exception:
            return None
    for word, value in number_words.items():
        if re.search(
            rf"\b(?:apenas|somente|so|s[oÃ³]|com)?\s*{word}\s+"
            r"(?:nomes?|registros?|linhas?|itens?|empresas?|clientes?)\b",
            low,
        ):
            return value
    return None


def _looks_like_header(row: List[str]) -> bool:
    joined = _plain(" ".join(row))
    markers = (
        "cliente",
        "empresa",
        "nome",
        "fantasia",
        "segmento",
        "status",
        "descricao",
        "descri",
        "item",
    )
    return any(marker in joined for marker in markers)


def _rows_from_source_context(
    source_context: Any,
    *,
    message: str,
    max_rows: int = 12,
    max_columns: int = 12,
) -> List[List[str]]:
    text = _source_context_text(source_context)
    if not text:
        return []

    rows: List[List[str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or "|" not in line:
            continue
        if line.startswith("[") or line.lower().startswith("fonte "):
            continue
        cells = [re.sub(r"\s+", " ", cell).strip() for cell in line.split("|")]
        cells = [cell[:180] for cell in cells if cell]
        if len(cells) < 2:
            continue
        rows.append(cells[:max_columns])
        if len(rows) >= 200:
            break

    if not rows:
        return []

    header: Optional[List[str]] = None
    data_start = 0
    for index, row in enumerate(rows[:20]):
        if _looks_like_header(row):
            header = row
            data_start = index + 1
            break
    limit = _requested_row_limit(message)
    if header is None:
        if limit is not None:
            return rows[:limit]
        header = rows[0]
        data_start = 1

    data_rows = [row for row in rows[data_start:] if row != header]
    if limit is not None:
        data_rows = data_rows[:limit]
    else:
        data_rows = data_rows[: max(1, max_rows - 1)]

    if not data_rows:
        return []
    return [header] + data_rows[: max(1, max_rows - 1)]


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
    source_context: Any = None,
) -> Dict[str, Any]:
    """Build a deterministic, bounded payload for the DOCIO generator."""

    raw = str(message or "").strip()
    fmt = str(decision.get("format") or "md").strip().lower()
    if fmt not in SUPPORTED_ARTIFACT_FORMATS:
        raise ValueError(f"unsupported_document_format:{fmt}")

    title = _title_for_format(fmt, raw)
    source_rows = _rows_from_source_context(source_context, message=raw)
    source_slides = _slides_from_source_context(source_context) if fmt in {"pptx", "docx", "pdf", "md"} else []
    source_required = _requires_bound_source_content(raw)
    has_source_signal = _source_context_has_attachment_signal(source_context)
    if source_required and not source_rows and not source_slides:
        raise ValueError("document_source_rows_required")

    rows: Optional[List[List[str]]] = source_rows or None
    if rows is None and fmt in {"xlsx", "csv"} and not source_required and not has_source_signal:
        rows = _spreadsheet_rows(raw)

    content = (
        "Artefato criado a partir de uma solicitação explícita do usuário.\n\n"
        f"Solicitação original: {raw[:4_000]}"
    )
    content = "Artefato criado a partir de uma solicitacao explicita do usuario."
    if source_rows:
        content += (
            "\n\nDados de origem: linhas extraidas do contexto de arquivo autorizado "
            "vinculado a esta conversa."
        )
    if source_slides:
        content += (
            "\n\nDados de origem: estrutura de slides extraida do PPTX autorizado "
            "vinculado a esta conversa."
        )
        if fmt in {"docx", "pdf", "md"}:
            content += "\n\n" + _source_slide_summary_text(source_slides)
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
        "slides": source_slides or None,
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
