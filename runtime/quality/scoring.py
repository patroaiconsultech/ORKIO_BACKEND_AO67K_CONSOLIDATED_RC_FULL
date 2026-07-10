from __future__ import annotations

from typing import Any, Dict, List

def ao70_score_checklist(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not results:
        return {"score": 100, "passed": True, "missing_items": [], "matched_items": []}

    total = sum(max(int(item.get("weight") or 1), 1) for item in results)
    got = sum(max(int(item.get("weight") or 1), 1) for item in results if item.get("matched"))
    score = int(round((got / max(total, 1)) * 100))
    missing = [str(item.get("key")) for item in results if not item.get("matched")]
    matched = [str(item.get("key")) for item in results if item.get("matched")]
    return {
        "score": score,
        "passed": score >= 85 and len(missing) == 0,
        "missing_items": missing,
        "matched_items": matched,
    }
