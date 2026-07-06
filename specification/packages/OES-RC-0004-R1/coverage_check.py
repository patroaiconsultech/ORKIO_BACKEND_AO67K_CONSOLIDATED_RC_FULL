#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "specification" / "packages" / "OES-RC-0004-R1"
PROJECTION = PKG / "contract_event_projection.json"

data = json.loads(PROJECTION.read_text(encoding="utf-8"))
records = data["records"]

capability_ids = [r["capability_id"] for r in records]
contract_ids = [r["command_contract"]["contract_id"] for r in records]
event_ids = [r["event_projection"]["event_id"] for r in records]

errors = []
if len(records) != 56:
    errors.append(f"expected 56 records, found {len(records)}")
if len(set(capability_ids)) != 56:
    errors.append("capability IDs are not unique")
if len(set(contract_ids)) != 56:
    errors.append("command contract IDs are not unique")
if len(set(event_ids)) != 56:
    errors.append("event IDs are not unique")

for r in records:
    if not r["command_contract"]["contract_id"].startswith("CON-"):
        errors.append(f"invalid contract id for {r['capability_id']}")
    if not r["event_projection"]["event_id"].startswith("EVT-"):
        errors.append(f"invalid event id for {r['capability_id']}")
    if r["command_contract"]["capability_id"] != r["capability_id"]:
        errors.append(f"contract capability mismatch for {r['capability_id']}")
    if r["event_projection"]["capability_id"] != r["capability_id"]:
        errors.append(f"event capability mismatch for {r['capability_id']}")

if errors:
    print("FAIL")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("PASS: 56 capabilities, 56 command contracts, 56 primary events")
