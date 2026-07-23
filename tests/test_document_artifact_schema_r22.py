from typing import Any, Dict, Optional

import pytest
from pydantic import Field, ValidationError

from schemas.document_artifacts import DocumentArtifactGenerateIn


class TrustedInternalDocumentArtifactGenerateIn(DocumentArtifactGenerateIn):
    source_plan: Optional[Dict[str, Any]] = Field(default=None)


def _base_payload():
    return {
        "format": "pptx",
        "title": "Apresentação",
        "content": "Conteúdo",
        "thread_id": "thread-1",
        "requested_agent_hint": "orkio",
    }


def test_public_schema_discards_builder_only_source_plan():
    payload = {
        **_base_payload(),
        "source_plan": {
            "planned_slide_count": 8,
            "minimum_slide_count": 6,
        },
    }

    model = DocumentArtifactGenerateIn.model_validate(payload)

    assert model.title == "Apresentação"
    assert "source_plan" not in DocumentArtifactGenerateIn.model_fields
    assert "source_plan" not in model.model_dump()


def test_trusted_internal_subclass_preserves_declared_source_plan():
    payload = {
        **_base_payload(),
        "source_plan": {
            "planned_slide_count": 8,
            "minimum_slide_count": 6,
        },
    }

    model = TrustedInternalDocumentArtifactGenerateIn.model_validate(payload)

    assert model.source_plan == {
        "planned_slide_count": 8,
        "minimum_slide_count": 6,
    }


def test_unknown_fields_remain_forbidden():
    with pytest.raises(ValidationError):
        DocumentArtifactGenerateIn.model_validate(
            {**_base_payload(), "runtime_owner": "attacker-controlled"}
        )


def test_format_aliases_are_preserved():
    model = DocumentArtifactGenerateIn.model_validate(
        {**_base_payload(), "format": "powerpoint"}
    )
    assert model.format == "pptx"
