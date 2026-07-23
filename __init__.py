from __future__ import annotations

from typing import Any, Mapping, Type


def sanitize_model_payload(model_cls: Type[Any], payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return only fields declared by the Pydantic model.

    This keeps strict validation enabled while preventing deterministic crashes
    caused by builder-only metadata such as source_plan.
    """
    model_fields = getattr(model_cls, "model_fields", None)
    if not isinstance(model_fields, dict):
        raise TypeError("model_cls must expose Pydantic v2 model_fields")

    allowed = set(model_fields.keys())
    return {key: value for key, value in dict(payload).items() if key in allowed}


def validate_document_payload(model_cls: Type[Any], payload: Mapping[str, Any]) -> Any:
    clean_payload = sanitize_model_payload(model_cls, payload)
    return model_cls.model_validate(clean_payload)
