from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


DocumentFormat = Literal["md", "csv", "xlsx", "docx", "pptx", "pdf"]


class DocumentArtifactGenerateIn(BaseModel):
    """Public DOCIO generation contract.

    Runtime identity, execution IDs and trusted limits remain absent.
    Unknown client fields are rejected by ``extra='forbid'``.

    ``source_plan`` is builder-only metadata. The public schema removes it
    before validation, while a trusted internal subclass that explicitly
    declares a ``source_plan`` field keeps it.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    format: DocumentFormat = "md"
    title: str = Field(default="Documento Orkio", min_length=1, max_length=180)
    content: Optional[str] = Field(default=None, max_length=200_000)
    filename: Optional[str] = Field(default=None, max_length=180)
    rows: Optional[List[Any]] = None
    slides: Optional[List[Any]] = None
    thread_id: Optional[str] = Field(default=None, max_length=128)
    requested_agent_hint: Optional[str] = Field(default=None, max_length=80)

    @model_validator(mode="before")
    @classmethod
    def remove_builder_only_metadata(cls, value: Any) -> Any:
        """Prevent backend planner metadata from crashing the public model.

        A trusted internal subclass may explicitly declare ``source_plan``.
        In that case the metadata is preserved for the internal execution
        contract. Every other unknown field remains forbidden.
        """
        if not isinstance(value, dict):
            return value

        if "source_plan" in cls.model_fields:
            return value

        sanitized: Dict[str, Any] = dict(value)
        sanitized.pop("source_plan", None)
        return sanitized

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
