from app.services.ocil.security import authority_for_agent


def test_chris_cannot_own_technical_governance() -> None:
    authority = authority_for_agent("chris")

    assert authority.can_create_technical_proposal is False
    assert authority.can_issue_technical_go_no_go is False
    assert "technical_governance" in authority.blocked_domains


def test_orion_cannot_write_repository() -> None:
    authority = authority_for_agent("orion")

    assert authority.can_write_repository is False
    assert "repository_write" in authority.blocked_domains
