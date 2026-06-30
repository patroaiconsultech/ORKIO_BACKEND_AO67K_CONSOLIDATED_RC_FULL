from pathlib import Path

ROOT = Path(__file__).resolve().parents.parent


def read(rel_path: str) -> str:
    path = ROOT / rel_path
    assert path.exists(), f"Missing required file: {rel_path}"
    return path.read_text(encoding="utf-8")


def test_required_documents_exist():
    required = [
        "docs/brand/CATEGORY.md",
        "docs/brand/POSITIONING.md",
        "docs/brand/MESSAGING.md",
        "docs/brand/VOICE_AND_TONE.md",
        "docs/brand/TERMINOLOGY.md",
        "docs/ENGINEERING_FRAMEWORK.md",
        "docs/CAPABILITY_TEMPLATE.md",
        "docs/ARCHITECTURE_SCORECARD.md",
        "docs/ENGINEERING_WORKFLOW.md",
        "docs/adr/ADR-0000-engineering-framework.md",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), f"Required file not found: {rel}"


def test_category_definition():
    content = read("docs/brand/CATEGORY.md")
    assert "Cognitive Operating System (COS)" in content
    assert "PatroAI" in content
    assert "Orkio" in content


def test_positioning():
    content = read("docs/brand/POSITIONING.md")
    assert "PatroAI" in content
    assert "Orkio" in content
    assert "Cognitive Operating System" in content


def test_terminology():
    content = read("docs/brand/TERMINOLOGY.md")
    for term in ["Mission", "Evidence", "Decision", "Outcome", "Capability"]:
        assert term in content
    for term in ["Chatbot", "AI Assistant", "Session"]:
        assert term in content
