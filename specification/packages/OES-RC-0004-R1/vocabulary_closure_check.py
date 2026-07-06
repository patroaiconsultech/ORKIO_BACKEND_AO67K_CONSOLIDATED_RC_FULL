#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "specification" / "packages" / "OES-RC-0004-R1"
vocab = set(json.loads((PKG / "reference_vocabulary.json").read_text(encoding="utf-8")))
payload = (PKG / "contract_event_projection.json").read_text(encoding="utf-8") + "\n" + (ROOT / "specification" / "OES-007_CONTRACT_EVENT_PROJECTION.md").read_text(encoding="utf-8")

refs = set(re.findall(r"\b[A-Z][A-Za-z]+Reference\b", payload))
forbidden = {"MembershipReference", "CapabilityBindingReference", "DelegationReference", "CorrelationReference"}

outside = sorted(refs - vocab)
bad = sorted(refs & forbidden)

if outside or bad:
    print("FAIL")
    if outside:
        print("References outside vocabulary:")
        for r in outside:
            print("-", r)
    if bad:
        print("Forbidden references:")
        for r in bad:
            print("-", r)
    raise SystemExit(1)

print(f"PASS: vocabulary closed ({len(refs)} reference types used)")
