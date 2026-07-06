#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
import sys

PKG_ID = "OES-RC-0003-R3"

ROOT = Path.cwd()
PKG = ROOT / "specification" / "packages" / PKG_ID
OES6 = ROOT / "specification" / "OES-006_CAPABILITY_CATALOG.md"
EXPECTED_JSON = PKG / "expected_capabilities.json"
VOCABULARY_JSON = PKG / "vocabulary_inventory.json"

def fail(msg: str) -> None:
    print(f"COVERAGE FAIL: {msg}")
    raise SystemExit(1)

def parse_reference_list(value: str) -> list[str]:
    if not value:
        return []
    raw = [x.strip().strip("`") for x in value.split(",")]
    refs = [x for x in raw if x and x.lower() != "none"]
    return refs

def parse_oes6(text: str) -> dict[str, dict]:
    entries = {}
    # Capability blocks generated in OES-006 use "#### CAP-XXX-000 — Name"
    blocks = re.split(r"\n#### ", "\n" + text)
    for block in blocks:
        if not block.startswith("CAP-"):
            continue
        first, *rest = block.splitlines()
        m = re.match(r"(CAP-[A-Z]+-\d{3})\s+—\s+(.+)", first.strip())
        if not m:
            fail(f"Malformed capability heading: {first}")
        cid, heading_name = m.group(1), m.group(2).strip()
        def field(label: str) -> str:
            mm = re.search(rf"- \*\*{re.escape(label)}:\*\* (.*)", block)
            return mm.group(1).strip() if mm else ""
        entries[cid] = {
            "capability_id": cid,
            "capability_name": field("Capability Name") or heading_name,
            "aggregate_root": field("Aggregate Root"),
            "authority": field("Authority"),
            "lifecycle": field("Lifecycle"),
            "related_invariants": [x.strip() for x in field("Applicable Aggregate Invariants").split(",") if x.strip()],
            "canonical_references": field("Canonical References"),
            "produced_references": field("Produced References"),
            "primary_contract": field("Primary Contract"),
            "primary_event": field("Primary Event"),
            "runtime_projection": field("Runtime Projection"),
            "verification_status": field("Verification Status"),
        }
    return entries

def load_vocabulary() -> set[str]:
    if not VOCABULARY_JSON.exists():
        fail(f"Missing canonical reference inventory: {VOCABULARY_JSON}")
    data = json.loads(VOCABULARY_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        fail("Canonical reference inventory must be a non-empty JSON list")
    vocabulary = set()
    for item in data:
        if not isinstance(item, str) or not item.endswith("Reference"):
            fail(f"Invalid canonical reference inventory item: {item!r}")
        vocabulary.add(item)
    return vocabulary

def main() -> None:
    if not EXPECTED_JSON.exists():
        fail(f"Missing expected capability model: {EXPECTED_JSON}")
    if not OES6.exists():
        fail(f"Missing OES-006 document: {OES6}")
    expected = json.loads(EXPECTED_JSON.read_text(encoding="utf-8"))
    vocabulary = load_vocabulary()
    found = parse_oes6(OES6.read_text(encoding="utf-8"))

    full_text = OES6.read_text(encoding="utf-8")
    bad_empty_precondition = "`none` " + "must be available"
    if bad_empty_precondition in full_text or "none " + "must be available" in full_text:
        fail("Invalid generated precondition: empty reference requirement")
    contracts = [v["primary_contract"] for v in found.values()]
    events = [v["primary_event"] for v in found.values()]
    runtimes = [v["runtime_projection"] for v in found.values()]
    if len(set(contracts)) != len(contracts):
        fail("Primary contracts are not unique")
    if len(set(events)) != len(events):
        fail("Primary events are not unique")
    if len(set(runtimes)) != len(runtimes):
        fail("Runtime projections are not unique")
    for cid, got_entry in found.items():
        produced_refs = got_entry.get("produced_references", "")
        parsed_produced_refs = parse_reference_list(produced_refs)
        if not parsed_produced_refs:
            fail(f"{cid} missing Produced References")
        if "when " + "applicable" in produced_refs:
            fail(f"{cid} has non-deterministic Produced References")
        outside_inventory = sorted(set(parsed_produced_refs) - vocabulary)
        if outside_inventory:
            fail(f"{cid} Produced References outside canonical inventory: {outside_inventory}")

    expected_ids = [x["capability_id"] for x in expected]
    if len(expected_ids) != 56:
        fail(f"Expected model should contain 56 capabilities, got {len(expected_ids)}")
    if len(set(expected_ids)) != len(expected_ids):
        fail("Duplicate IDs in expected model")

    found_ids = sorted(found)
    missing = sorted(set(expected_ids) - set(found_ids))
    extra = sorted(set(found_ids) - set(expected_ids))
    if missing:
        fail(f"Missing capability IDs: {missing}")
    if extra:
        fail(f"Extra capability IDs: {extra}")

    exp_by_id = {x["capability_id"]: x for x in expected}
    for cid, exp in exp_by_id.items():
        got = found[cid]
        for key in ["capability_name", "aggregate_root", "authority", "lifecycle", "canonical_references"]:
            if got[key] != exp[key]:
                fail(f"{cid} mismatch for {key}: expected {exp[key]!r}, got {got[key]!r}")
        if got["related_invariants"] != exp["related_invariants"]:
            fail(f"{cid} mismatch for related_invariants: expected {exp['related_invariants']!r}, got {got['related_invariants']!r}")
        for key in ["primary_contract", "primary_event", "runtime_projection", "verification_status"]:
            if not got[key]:
                fail(f"{cid} missing required OES-006 field {key}")

    print("COVERAGE PASS: 56/56 capabilities match OES-005/R4 canonical model")
    print("VOCABULARY PASS: Produced References are contained in canonical reference inventory")

if __name__ == "__main__":
    main()
