#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "specification" / "packages" / "OES-RC-0005-R4"
REQUIRED_CLASSES = {"PUBLIC","INTERNAL","FOUNDER_PRIVATE","SENSITIVE","STRATEGIC_CONFIDENTIAL","DO_NOT_USE"}
ALLOWED_SOURCE_USE = {"none","metadata_only_without_content_access"}

def main() -> int:
    errors = []
    schema = json.loads((PKG / "classification_schema_template.json").read_text(encoding="utf-8"))
    if schema.get("additionalProperties") is not False:
        errors.append("Schema additionalProperties must be false.")
    props = schema.get("properties", {})
    expected_consts = {
        "classification": "PRIVATE_SOURCE_CANDIDATE",
        "raw_content_included": False,
        "direct_publication_allowed": False,
        "public_repository_allowed": False,
        "content_access_allowed": False,
        "requires_triage": True,
        "requires_sanitization": True,
        "requires_founder_approval_before_use": True,
    }
    for key, expected in expected_consts.items():
        if props.get(key, {}).get("const") != expected:
            errors.append(f"Schema property {key} must have const {expected!r}.")
    if set(props.get("allowed_current_use", {}).get("enum", [])) != ALLOWED_SOURCE_USE:
        errors.append("Schema allowed_current_use enum must be none|metadata_only_without_content_access.")
    matrix = json.loads((PKG / "context_classification_matrix.json").read_text(encoding="utf-8"))
    classes = {item.get("class_id") for item in matrix.get("classes", [])}
    missing = REQUIRED_CLASSES - classes
    if missing:
        errors.append(f"Missing classes: {sorted(missing)}")
    for item in matrix.get("classes", []):
        cid = item.get("class_id")
        if item.get("raw_content_allowed") is not False:
            errors.append(f"raw_content_allowed must be false for {cid}")
        if item.get("founder_approval_required") is not True:
            errors.append(f"founder_approval_required must be true for {cid}")
    policy = json.loads((PKG / "context_usage_policy.json").read_text(encoding="utf-8"))
    if policy.get("default_state") != "DENY_BY_DEFAULT":
        errors.append("Policy default_state must be DENY_BY_DEFAULT")
    if policy.get("learning_rule") is None:
        errors.append("Policy must define safe learning rule.")
    register = json.loads((PKG / "private_source_register_seed.json").read_text(encoding="utf-8"))
    for source in register.get("sources", []):
        sid = source.get("source_id")
        if source.get("classification") != "PRIVATE_SOURCE_CANDIDATE":
            errors.append(f"{sid}: source candidate must remain PRIVATE_SOURCE_CANDIDATE")
        if source.get("raw_content_included") is not False:
            errors.append(f"{sid}: raw_content_included must be false")
        if source.get("direct_publication_allowed") is not False:
            errors.append(f"{sid}: direct_publication_allowed must be false")
        if source.get("public_repository_allowed") is not False:
            errors.append(f"{sid}: public_repository_allowed must be false")
        if source.get("content_access_allowed") is not False:
            errors.append(f"{sid}: content_access_allowed must be false")
        if source.get("requires_founder_approval_before_use") is not True:
            errors.append(f"{sid}: founder approval before use must be true")
        if source.get("allowed_current_use") not in ALLOWED_SOURCE_USE:
            errors.append(f"{sid}: invalid allowed_current_use {source.get('allowed_current_use')}")
    if errors:
        print("classification_check: FAIL")
        for err in errors:
            print(err)
        return 1
    print("classification_check: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
