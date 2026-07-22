import os

from services.orion_premium.vision_gateway import analyze_image, is_supported_image


def test_image_detection_by_mime_and_extension():
    assert is_supported_image("photo.bin", "image/jpeg")
    assert is_supported_image("photo.png", None)
    assert not is_supported_image("report.pdf", "application/pdf")


def test_vision_fails_closed_when_disabled(monkeypatch):
    monkeypatch.setenv("ORKIO_VISION_PIPELINE_ENABLED", "false")
    result = analyze_image(filename="photo.jpg", raw=b"fake", mime_type="image/jpeg")
    assert result.processed is False
    assert result.mode == "image_vision_unavailable"
    assert result.reason == "vision_pipeline_disabled"
