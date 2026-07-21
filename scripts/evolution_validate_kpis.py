"""Readonly validation for the Evolution Intelligence KPI registry."""

from __future__ import annotations

import json

from app.evolution.intelligence.governance import (
    load_evolution_governance_config,
    validate_evolution_governance_config,
)
from app.evolution.intelligence.kpi_registry import registry_payload


def main() -> int:
    registry = registry_payload()
    try:
        governance = validate_evolution_governance_config(
            load_evolution_governance_config()
        )
        governance_error = None
    except Exception as exc:
        governance = None
        governance_error = {
            "error_type": exc.__class__.__name__,
            "reason": str(exc),
        }

    passed = (
        not registry["definition_incomplete"]
        and registry["auto_apply_enabled"] is False
        and governance_error is None
    )
    result = {
        "package": "ORKIO-EVOLUTION-INTELLIGENCE-R1.1",
        "registry": registry,
        "governance": governance,
        "governance_error": governance_error,
        "write_executed": False,
        "passed": passed,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
