from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(rel_path: str) -> str:
    path = ROOT / rel_path
    assert path.exists(), f"Missing required file: {rel_path}"
    return path.read_text(encoding="utf-8")


def test_domain_model_documents_exist():
    required = [
        "docs/capabilities/domain_model.md",
        "docs/domain/ORKIO_DOMAIN_MODEL.md",
        "docs/domain/ORKIO_UBIQUITOUS_LANGUAGE_SEED.md",
        "docs/adr/ADR-0001-mission-domain-model.md",
    ]

    for rel in required:
        assert (ROOT / rel).exists(), f"Required file not found: {rel}"


def test_mission_is_declared_as_aggregate_root():
    content = read("docs/domain/ORKIO_DOMAIN_MODEL.md")

    assert "Mission is the aggregate root" in content
    assert "Conversation is transient. Mission is persistent." in content
    assert "Conversation is an interaction channel" in content


def test_required_domain_concepts_are_defined():
    content = read("docs/domain/ORKIO_DOMAIN_MODEL.md")

    required_terms = [
        "Strategic Intent",
        "Mission",
        "Conversation",
        "Evidence",
        "Hypothesis",
        "Decision",
        "Outcome",
        "Learning",
        "Mission Health",
        "Workspace",
        "Organization",
        "Agent",
    ]

    for term in required_terms:
        assert term in content, f"Missing domain concept: {term}"


def test_domain_ownership_rules_are_present():
    content = read("docs/domain/ORKIO_DOMAIN_MODEL.md")

    expected_rules = [
        "Every persistent artifact belongs to exactly one Mission.",
        "Conversations belong to Missions.",
        "Documents belong to Missions.",
        "Evidence belongs to Missions.",
        "Hypotheses belong to Missions.",
        "Decisions belong to Missions.",
        "Outcomes belong to Missions.",
        "Learning is derived from Mission events.",
        "The LLM never owns Mission state.",
    ]

    for rule in expected_rules:
        assert rule in content, f"Missing ownership rule: {rule}"


def test_adr_records_mission_centered_decision():
    content = read("docs/adr/ADR-0001-mission-domain-model.md")

    assert "Accepted" in content
    assert "Mission is the aggregate root" in content
    assert "The LLM never owns Mission state" in content
    assert "conceptual architecture only" in content
