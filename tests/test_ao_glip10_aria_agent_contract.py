from pathlib import Path

from runtime.agent_registry import canonical_agent_profile, registry_payload
from runtime.glip_aria_agent_contract import (
    ARIA_AGENT_SLUG,
    complete_patroai_selector_agents,
    ensure_glip_aria_agent,
    filter_patroai_selector_agents,
    selector_agent_slugs,
)


def test_aria_registry_profile_is_internal_and_not_team_member():
    profile = canonical_agent_profile("aria")

    assert profile is not None
    assert profile.slug == ARIA_AGENT_SLUG
    assert profile.display_name == "Aria"
    assert profile.internal_agent is True
    assert profile.public_agent is False
    assert profile.team_default is False
    assert profile.team_optional is False
    assert profile.voice_id == "marin"


def test_public_registry_hides_aria_and_internal_registry_exposes_it():
    public_slugs = {item["slug"] for item in registry_payload(include_internal=False)["items"]}
    internal_slugs = {item["slug"] for item in registry_payload(include_internal=True)["items"]}

    assert ARIA_AGENT_SLUG not in public_slugs
    assert ARIA_AGENT_SLUG in internal_slugs


def test_patroai_selector_hides_aria_from_non_admin_and_keeps_for_admin():
    items = [
        {"agent_key": "orkio", "name": "Orkio"},
        {"agent_key": "aria", "name": "Aria"},
    ]

    regular = filter_patroai_selector_agents(items, privileged=False)
    admin = filter_patroai_selector_agents(items, privileged=True)

    assert [item["agent_key"] for item in regular] == ["orkio"]
    assert [item["agent_key"] for item in admin] == ["orkio", "aria"]


def test_selector_required_slugs_add_aria_only_for_admin():
    assert ARIA_AGENT_SLUG not in selector_agent_slugs(privileged=False)
    assert ARIA_AGENT_SLUG in selector_agent_slugs(privileged=True)


def test_selector_completion_adds_admin_only_aria_fallback():
    def build(org, slug, meta):
        return {"org_slug": org, "agent_key": slug, "name": slug.title(), **meta}

    regular = complete_patroai_selector_agents(
        [],
        privileged=False,
        org="tenant-a",
        roster={},
        build_roster_payload=build,
    )
    admin = complete_patroai_selector_agents(
        [],
        privileged=True,
        org="tenant-a",
        roster={},
        build_roster_payload=build,
    )

    assert ARIA_AGENT_SLUG not in {item["agent_key"] for item in regular}
    assert ARIA_AGENT_SLUG in {item["agent_key"] for item in admin}


def test_seed_contract_uses_canonical_profile_without_becoming_default():
    calls = []

    def capture(**kwargs):
        calls.append(kwargs)

    ensure_glip_aria_agent(capture)

    assert len(calls) == 1
    payload = calls[0]
    assert payload["canonical_name"] == "Aria"
    assert payload["voice_id"] == "marin"
    assert payload["is_default"] is False
    assert "GLIP" in payload["aliases"]
    assert "inteligência operacional" in payload["description"].lower()


def test_main_integration_stays_thin_and_uses_contract_helpers():
    main_source = (Path(__file__).resolve().parents[1] / "main.py").read_text(encoding="utf-8")

    assert "ensure_glip_aria_agent(upsert)" in main_source
    assert "complete_patroai_selector_agents(" in main_source
    assert '["orkio", "team", "chris", "orion"]' not in main_source
    assert "ARIA_SYSTEM_PROMPT =" not in main_source
