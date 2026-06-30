from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = [
    "docs/ORKIO_OS_ARCHITECTURE.md",
    "docs/Platform_Core.md",
    "docs/Cognitive_Core.md",
    "docs/Experience_Core.md",
    "docs/Governance_Core.md",
    "docs/Mission_Runtime.md",
    "docs/Constitution.md",
]

REQUIRED_TERMS = {
    "docs/ORKIO_OS_ARCHITECTURE.md": [
        "ORKIO OS 1.0",
        "Platform Core",
        "Cognitive Core",
        "Experience Core",
        "Governance Core",
        "Mission Runtime",
        "Constitution",
    ],
    "docs/Platform_Core.md": ["FastAPI", "SSE", "streaming", "Metrics", "Observability", "Security"],
    "docs/Cognitive_Core.md": ["Perception", "Working Memory", "Hypothesis Engine", "Evidence Engine", "Learning"],
    "docs/Experience_Core.md": ["Landing", "Onboarding", "Conversation UX", "Executive dashboard", "Personalization"],
    "docs/Governance_Core.md": ["Constitution", "Proposal Engine", "Approval Engine", "Quality Gates", "Rollback"],
    "docs/Mission_Runtime.md": ["mission", "objective", "stage", "hypotheses", "next_best_action"],
    "docs/Constitution.md": ["Article I", "Article X", "understand, decide and build", "Human Authority", "Governed Evolution"],
}

def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def test_required_docs_exist():
    missing = [p for p in REQUIRED_DOCS if not (ROOT / p).exists()]
    assert not missing, f"Missing ORKIO OS architecture docs: {missing}"

def test_required_terms_present():
    for path, terms in REQUIRED_TERMS.items():
        content = _read(path)
        missing_terms = [term for term in terms if term not in content]
        assert not missing_terms, f"{path} missing required terms: {missing_terms}"

def test_architecture_scope_is_documentation_only():
    content = _read("docs/ORKIO_OS_ARCHITECTURE.md")
    assert "must not change runtime behavior" in content
