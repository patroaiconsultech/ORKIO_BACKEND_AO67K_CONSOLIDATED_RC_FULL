#!/usr/bin/env python3
"""AO-GLIP10 offline verifier for rebased Aria registry/admin visibility."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    main = (ROOT / "main.py").read_text(encoding="utf-8")
    registry = (ROOT / "runtime" / "agent_registry.py").read_text(encoding="utf-8")
    contract = (ROOT / "runtime" / "glip_aria_agent_contract.py").read_text(encoding="utf-8")

    checks = {
        "thin_main_import": "from .runtime.glip_aria_agent_contract import complete_patroai_selector_agents, ensure_glip_aria_agent" in main,
        "aria_seed_wired": "ensure_glip_aria_agent(upsert)" in main,
        "selector_policy_wired": "return complete_patroai_selector_agents(" in main,
        "legacy_selector_hardcode_removed": '["orkio", "team", "chris", "orion"]' not in main,
        "aria_registry_profile": '"aria": CanonicalAgentProfile(' in registry,
        "aria_not_team_default": "team_default=False" in registry,
        "aria_admin_only_policy": "ADMIN_ONLY_SELECTOR_AGENT_SLUGS" in contract,
        "aria_prompt_outside_main": "ARIA_SYSTEM_PROMPT =" not in main,
    }

    for name, passed in checks.items():
        require(passed, f"FAILED: {name}")

    print(json.dumps({"patch": "AO-GLIP10", "passed": True, "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
