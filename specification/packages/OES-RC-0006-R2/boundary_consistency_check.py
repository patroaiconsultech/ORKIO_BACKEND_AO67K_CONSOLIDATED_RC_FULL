#!/usr/bin/env python3
from pathlib import Path
import json

PACKAGE = Path(__file__).resolve().parent
MAPPING = PACKAGE / "handler_boundary_mapping.json"

REQUIRED_PORTS = {
    "CommandDispatchPort",
    "PolicyDecisionPort",
    "IdempotencyStorePort",
    "ReferenceResolutionPort",
    "AggregateRepositoryPort",
    "EventOutboxPort",
    "AuditRecordPort",
    "ClockPort",
    "TraceContextPort",
}

def main() -> int:
    data = json.loads(MAPPING.read_text(encoding="utf-8"))
    errors = []
    for r in data.get("handler_boundaries", []):
        hid = r["handler_boundary"]["handler_id"]
        hname = r["handler_boundary"]["handler_name"]
        cid = r["input_contract"]["command_contract_id"]
        eid = r["output_event"]["event_id"]
        if not hid.startswith("HND-"):
            errors.append(f"Invalid handler id: {hid}")
        if not cid.startswith("CON-"):
            errors.append(f"Invalid command id: {cid}")
        if not eid.startswith("EVT-"):
            errors.append(f"Invalid event id: {eid}")
        if not hname.endswith("Handler"):
            errors.append(f"Handler name must end with Handler: {hname}")
        missing_ports = REQUIRED_PORTS.difference(set(r.get("required_ports", [])))
        if missing_ports:
            errors.append(f"{hid} missing ports: {sorted(missing_ports)}")
        if r["handler_boundary"].get("implementation_status") != "not_implemented_specification_only":
            errors.append(f"{hid} has invalid implementation status")
    if errors:
        print("boundary_consistency_check: FAIL")
        for e in errors:
            print(e)
        return 1
    print("boundary_consistency_check: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
