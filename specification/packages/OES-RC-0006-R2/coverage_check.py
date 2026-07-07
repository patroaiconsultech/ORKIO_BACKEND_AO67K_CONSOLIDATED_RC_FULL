#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
MAPPING = PACKAGE / "handler_boundary_mapping.json"

def main() -> int:
    data = json.loads(MAPPING.read_text(encoding="utf-8"))
    records = data.get("handler_boundaries", [])
    handler_ids = [r["handler_boundary"]["handler_id"] for r in records]
    command_ids = [r["input_contract"]["command_contract_id"] for r in records]
    event_ids = [r["output_event"]["event_id"] for r in records]
    errors = []
    if len(records) != 56:
        errors.append(f"Expected 56 handler boundaries, found {len(records)}")
    if len(set(handler_ids)) != 56:
        errors.append("Handler IDs are not unique")
    if len(set(command_ids)) != 56:
        errors.append("Command contract IDs are not unique")
    if len(set(event_ids)) != 56:
        errors.append("Event IDs are not unique")
    if len(data.get("runtime_boundaries", [])) != 8:
        errors.append(f"Expected 8 runtime boundaries, found {len(data.get('runtime_boundaries', []))}")
    if errors:
        print("coverage_check: FAIL")
        for e in errors:
            print(e)
        return 1
    print("coverage_check: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
