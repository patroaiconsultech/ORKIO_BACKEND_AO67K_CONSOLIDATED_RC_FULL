\
from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional

from .checklist import ao70_expected_checklist
from .intent_analyzer import ao70_analyze_intent
from .scoring import ao70_score_checklist

def _norm(text: Any) -> str:
    raw = str(text or "").lower()
    raw = unicodedata.normalize("NFKD", raw)
    raw = "".join(ch for ch in raw if not unicodedata.combining(ch))
    return raw

def _has_any(text: str, terms: List[str]) -> bool:
    return any(_norm(term) in text for term in list(terms or []))

def _has_number_or_formula(text: str) -> bool:
    return bool(re.search(r"(\d+[\d\.,]*\s*%?|\br\$\s*\d+|\bus\$\s*\d+|\b=\b|\bresultado\b|\bcalculo\b|\bcálculo\b)", text, re.I))

def ao70_validate_response(prompt: Any, answer: Any, *, response_control: Optional[str] = None) -> Dict[str, Any]:
    intent = ao70_analyze_intent(prompt, response_control=response_control)
    if not intent.get("applies"):
        return {
            "version": intent.get("version"),
            "applies": False,
            "score": 100,
            "passed": True,
            "missing_items": [],
            "matched_items": [],
            "intent": intent,
        }

    text = _norm(answer)
    checklist = ao70_expected_checklist(prompt)

    results: List[Dict[str, Any]] = []
    for item in checklist:
        terms = list(item.get("answer_terms") or [])
        matched = _has_any(text, terms)
        # Calculation items need at least some numeric/formula signal in the answer.
        if item.get("key") in {"operating_profit", "margin", "runway", "ltv", "cac", "ltv_cac_ratio"}:
            matched = matched and _has_number_or_formula(text)
        results.append({**item, "matched": bool(matched)})

    scoring = ao70_score_checklist(results)

    # Penalize generic onboarding-style answers in executive mode.
    generic_patterns = [
        "para começar, me diga",
        "para comecar, me diga",
        "conte um pouco",
        "me fale mais",
        "preciso entender melhor",
        "qual é o seu objetivo",
    ]
    generic = any(p in text for p in generic_patterns)
    score = int(scoring["score"])
    if generic:
        score = min(score, 60)

    passed = bool(score >= 85 and not scoring["missing_items"] and not generic)

    return {
        "version": intent.get("version"),
        "applies": True,
        "intent": intent,
        "score": score,
        "passed": passed,
        "generic_onboarding_detected": generic,
        "missing_items": scoring["missing_items"],
        "matched_items": scoring["matched_items"],
        "checklist": results,
    }
