#!/usr/bin/env python3
from pathlib import Path
import json

PACKAGE = Path(__file__).resolve().parent
MODEL = PACKAGE / "persistence_state_model.json"

def main() -> int:
    data = json.loads(MODEL.read_text(encoding="utf-8"))
    states = data.get("state_models", [])
    groups = data.get("state_repository_groups", [])
    errors = []
    if len(states) != 56:
        errors.append(f"Expected 56 state models, found {len(states)}")
    if len({s["state_model_id"] for s in states}) != 56:
        errors.append("State model IDs are not unique")
    if len({s["handler_id"] for s in states}) != 56:
        errors.append("Handler IDs are not unique")
    if len(groups) != 8:
        errors.append(f"Expected 8 state repository groups, found {len(groups)}")
    if errors:
        print("coverage_check: FAIL")
        for e in errors:
            print(e)
        return 1
    print("coverage_check: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
