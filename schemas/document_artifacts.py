from __future__ import annotations

from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


DocumentFormat = Literal["md", "csv", "xlsx", "docx", "pptx", "pdf"]


class DocumentArtifactGenerateIn(BaseModel):
    """Public DOCIO generation contract.

    Runtime identity, execution IDs and trusted limits are intentionally absent.
    Any such client supplied fields are rejected by ``extra='forbid'``.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    format: DocumentFormat = "md"
    title: str = Field(default="Documento Orkio", min_length=1, max_length=180)
    content: Optional[str] = Field(default=None, max_length=200_000)
    filename: Optional[str] = Field(default=None, max_length=180)
    rows: Optional[List[Any]] = None
    thread_id: Optional[str] = Field(default=None, max_length=128)
    requested_agent_hint: Optional[str] = Field(default=None, max_length=80)

    @field_validator("format", mode="before")
    @classmethod
    def normalize_format(cls, value: Any) -> str:
        raw = str(value or "md").strip().lower().lstrip(".")
        aliases = {
            "markdown": "md",
            "excel": "xlsx",
            "word": "docx",
            "powerpoint": "pptx",
        }
        return aliases.get(raw, raw)
