from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.py"

def test_sse_lifecycle_audit_markers_present():
    content = MAIN.read_text(encoding="utf-8", errors="ignore")

    required = [
        "AO29_BEFORE_FIRST_STATUS_YIELD",
        "SSE_STATUS_YIELD_ATTEMPT",
        "AO29_STREAM_EXIT",
        "SSE_STREAM_EXIT_REACHED",
        "CLIENT_CANCELLED_BEFORE_FIRST_EVENT",
    ]

    for marker in required:
        assert marker in content, f"Missing SSE lifecycle audit marker: {marker}"


def test_sse_audit_uses_warning_level_for_railway_visibility():
    content = MAIN.read_text(encoding="utf-8", errors="ignore")

    assert 'logger.warning("SSE_STATUS_YIELD_ATTEMPT' in content
    assert 'logger.warning("SSE_STREAM_EXIT_REACHED' in content
    assert 'logger.warning("CLIENT_CANCELLED_BEFORE_FIRST_EVENT' in content
