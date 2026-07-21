"""
AO-GLIP10 — Canonical Aria agent contract.

Keeps the GLIP/Aria seed and PatroAI selector visibility policy outside
``main.py``. Aria is globally registered as an internal agent, visible in the
PatroAI selector only to admin-authorized users. The standalone GLIP surface
continues to lock the experience to Aria independently.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple

try:
    from ..aria_profile import (
        ARIA_ALIASES,
        ARIA_CANONICAL_NAME,
        ARIA_DESCRIPTION,
        ARIA_SYSTEM_PROMPT,
        ARIA_VOICE_ID,
    )
except ImportError:  # pragma: no cover - supports direct ``runtime`` test imports
    from aria_profile import (  # type: ignore
        ARIA_ALIASES,
        ARIA_CANONICAL_NAME,
        ARIA_DESCRIPTION,
        ARIA_SYSTEM_PROMPT,
        ARIA_VOICE_ID,
    )

from .agent_registry import canonical_agent_slug


ARIA_AGENT_SLUG = "aria"

# Preserve the current selector baseline. Aria is intentionally additive only
# for privileged PatroAI users and is never added to Team automatically.
BASE_SELECTOR_AGENT_SLUGS: Tuple[str, ...] = ("orkio", "team", "chris", "orion")
ADMIN_ONLY_SELECTOR_AGENT_SLUGS: Tuple[str, ...] = (ARIA_AGENT_SLUG,)


def ensure_glip_aria_agent(upsert: Callable[..., Any]) -> None:
    """Seed Aria through the caller-owned conservative upsert transaction."""

    upsert(
        canonical_name=ARIA_CANONICAL_NAME,
        aliases=list(ARIA_ALIASES),
        description=ARIA_DESCRIPTION,
        system_prompt=ARIA_SYSTEM_PROMPT,
        voice_id=ARIA_VOICE_ID,
        is_default=False,
    )


def selector_agent_slugs(*, privileged: bool) -> Tuple[str, ...]:
    """Return required selector slugs for the current PatroAI authority."""

    if privileged:
        return BASE_SELECTOR_AGENT_SLUGS + ADMIN_ONLY_SELECTOR_AGENT_SLUGS
    return BASE_SELECTOR_AGENT_SLUGS


def _selector_item_slug(item: Dict[str, Any]) -> str:
    candidates: Sequence[Any] = (
        item.get("agent_key"),
        item.get("slug"),
        item.get("name"),
        item.get("display_name"),
        item.get("legacy_name"),
        item.get("id"),
    )
    for candidate in candidates:
        slug = canonical_agent_slug(candidate, default="", allow_unknown=True) or ""
        if slug:
            return str(slug).strip().lower()
    return ""


def filter_patroai_selector_agents(
    items: Iterable[Dict[str, Any]],
    *,
    privileged: bool,
) -> List[Dict[str, Any]]:
    """Hide admin-only agents from non-admin PatroAI selector responses."""

    rows = [dict(item) for item in list(items or []) if isinstance(item, dict)]
    if privileged:
        return rows
    return [item for item in rows if _selector_item_slug(item) != ARIA_AGENT_SLUG]


def complete_patroai_selector_agents(
    items: Iterable[Dict[str, Any]],
    *,
    privileged: bool,
    org: str,
    roster: Dict[str, Dict[str, Any]],
    build_roster_payload: Callable[[str, str, Dict[str, Any]], Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Complete the selector baseline and enforce Aria's admin-only visibility."""

    rows = [dict(item) for item in list(items or []) if isinstance(item, dict)]
    present = {_selector_item_slug(item) for item in rows}
    for slug in selector_agent_slugs(privileged=privileged):
        if slug not in present:
            rows.append(build_roster_payload(org, slug, dict(roster.get(slug) or {})))
    return filter_patroai_selector_agents(rows, privileged=privileged)
