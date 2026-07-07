#!/usr/bin/env python3
from pathlib import Path
import json

PACKAGE = Path(__file__).resolve().parent
MAPPING = PACKAGE / "handler_boundary_mapping.json"

def main() -> int:
    data = json.loads(MAPPING.read_text(encoding="utf-8"))
    vocab = set(data.get("reference_vocabulary", []))
    errors = []
    for r in data.get("handler_boundaries", []):
        hid = r["handler_boundary"]["handler_id"]
        refs = set(r["input_contract"].get("reference_fields_allowed", []))
        produced = set(r["output_event"].get("produced_reference_types", []))
        for ref in sorted(refs | produced):
            if ref not in vocab:
                errors.append(f"{hid} uses reference outside vocabulary: {ref}")
    if errors:
        print("vocabulary_closure_check: FAIL")
        for e in errors:
            print(e)
        return 1
    print("vocabulary_closure_check: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
