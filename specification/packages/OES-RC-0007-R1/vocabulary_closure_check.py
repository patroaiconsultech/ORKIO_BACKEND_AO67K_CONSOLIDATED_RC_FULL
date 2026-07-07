#!/usr/bin/env python3
from pathlib import Path
import json

PACKAGE = Path(__file__).resolve().parent
MODEL = PACKAGE / "persistence_state_model.json"

def main() -> int:
    data = json.loads(MODEL.read_text(encoding="utf-8"))
    vocab = set(data.get("reference_vocabulary", []))
    errors = []
    for s in data.get("state_models", []):
        ref = s.get("primary_reference_type")
        if ref and ref not in vocab:
            errors.append(f"{s['state_model_id']} primary_reference_type outside vocabulary: {ref}")
    if errors:
        print("vocabulary_closure_check: FAIL")
        for e in errors:
            print(e)
        return 1
    print("vocabulary_closure_check: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
