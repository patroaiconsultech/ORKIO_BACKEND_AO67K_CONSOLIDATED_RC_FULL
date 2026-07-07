#!/usr/bin/env python3
from pathlib import Path
import json

PACKAGE = Path(__file__).resolve().parent
MODEL = PACKAGE / "persistence_state_model.json"

REQUIRED_FIELDS = {
    "state_id",
    "state_version",
    "aggregate_reference",
    "lifecycle_status",
    "created_at",
    "updated_at",
    "last_event_id",
    "last_command_id",
    "correlation_id",
    "causation_id",
    "audit_record_reference",
}

def main() -> int:
    data = json.loads(MODEL.read_text(encoding="utf-8"))
    errors = []
    for s in data.get("state_models", []):
        sid = s["state_model_id"]
        if not sid.startswith("STM-"):
            errors.append(f"Invalid state model id: {sid}")
        if not s["repository_port"].endswith("RepositoryPort"):
            errors.append(f"{sid} invalid repository port: {s['repository_port']}")
        missing = REQUIRED_FIELDS.difference(set(s.get("required_state_fields", [])))
        if missing:
            errors.append(f"{sid} missing state fields: {sorted(missing)}")
        if s.get("persistence_status") != "not_implemented_specification_only":
            errors.append(f"{sid} invalid persistence status")
        privacy = s.get("privacy_policy", {})
        if privacy.get("raw_private_content_allowed") is not False:
            errors.append(f"{sid} allows raw private content")
        if privacy.get("founder_private_context_storage_allowed") is not False:
            errors.append(f"{sid} allows founder private context storage")
    if errors:
        print("state_consistency_check: FAIL")
        for e in errors:
            print(e)
        return 1
    print("state_consistency_check: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
