from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional


PREMIUM_AGENT_STANDARD: Dict[str, Any] = {
    "version": "AO67G-v1",
    "public_speaker": "Orkio",
    "internal_specialists_are_visible": False,
    "minimum_quality_gates": [
        "truthfulness",
        "specificity",
        "usefulness",
        "risk_awareness",
        "next_step",
        "privacy_and_safety",
        "no_internal_agent_leakage",
        "no_unapproved_self_evolution",
    ],
    "response_contract": {
        "must_be": [
            "claro",
            "preciso",
            "executivo",
            "humano",
            "prudente",
            "auditavel",
            "acionavel",
        ],
        "must_not_be": [
            "vago",
            "performatico",
            "autoritario",
            "promessa_sem_lastro",
            "exposicao_de_bastidor",
            "catalogo_de_agentes_internos",
        ],
    },
    "protected_internal_names": [
        "Chris",
        "Orion",
        "CFO",
        "CTO",
        "Planner",
        "Auditor",
        "Founder Handoff",
        "Runtime",
        "Decision Mesh",
    ],
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _lower(value: Any) -> str:
    return _text(value).lower()


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    text_l = _lower(text)
    return any(_lower(term) in text_l for term in terms if _text(term))


def evaluate_premium_response(
    *,
    user_message: str,
    draft_response: str,
    public_surface: bool = True,
    agent_name: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Evaluate whether a draft response meets the AO67G premium standard.

    This is intentionally deterministic and side-effect free:
    - no LLM calls
    - no database access
    - no network
    - no writes
    """

    context = deepcopy(context or {})
    user_message_l = _lower(user_message)
    draft = _text(draft_response)
    draft_l = _lower(draft)

    protected_names: List[str] = list(PREMIUM_AGENT_STANDARD["protected_internal_names"])
    leaked_names = [name for name in protected_names if name.lower() in draft_l]

    self_evolution_terms = [
        "commit",
        "deploy",
        "branch",
        "pull request",
        "pr",
        "migration",
        "escrita real",
        "apliquei",
        "fiz deploy",
        "fiz commit",
    ]

    dangerous_certainty = [
        "garanto 100%",
        "perfeito sem risco",
        "infalível",
        "nunca falha",
        "sem risco algum",
    ]

    has_next_step = _contains_any(
        draft_l,
        ["próximo passo", "vamos começar", "recomendo", "sugiro", "para avançar", "checklist"],
    )
    has_specificity = len(draft.split()) >= 12
    asks_context_when_needed = True
    if any(term in user_message_l for term in ["quero", "preciso", "me ajuda", "desenvolver", "criar"]):
        asks_context_when_needed = _contains_any(
            draft_l,
            ["me diga", "qual", "quais", "contexto", "objetivo", "resultado", "prazo", "área"],
        ) or has_next_step

    no_internal_leakage = not leaked_names if public_surface else True
    no_unapproved_evolution = not (
        _contains_any(draft_l, self_evolution_terms)
        and not bool(context.get("founder_authorization_present"))
    )
    no_false_perfection = not _contains_any(draft_l, dangerous_certainty)

    passed = all([
        bool(draft),
        has_specificity,
        has_next_step,
        asks_context_when_needed,
        no_internal_leakage,
        no_unapproved_evolution,
        no_false_perfection,
    ])

    blocked_by: List[str] = []
    if not draft:
        blocked_by.append("empty_response")
    if not has_specificity:
        blocked_by.append("response_too_generic")
    if not has_next_step:
        blocked_by.append("missing_next_step")
    if not asks_context_when_needed:
        blocked_by.append("missing_context_discovery")
    if not no_internal_leakage:
        blocked_by.append("internal_agent_leakage:" + ",".join(leaked_names))
    if not no_unapproved_evolution:
        blocked_by.append("unapproved_self_evolution_language")
    if not no_false_perfection:
        blocked_by.append("false_perfection_or_infallibility_claim")

    return {
        "version": PREMIUM_AGENT_STANDARD["version"],
        "passed": passed,
        "public_speaker": PREMIUM_AGENT_STANDARD["public_speaker"],
        "resolved_agent_name": "Orkio" if public_surface else _text(agent_name or "Orkio"),
        "public_surface": public_surface,
        "has_specificity": has_specificity,
        "has_next_step": has_next_step,
        "asks_context_when_needed": asks_context_when_needed,
        "no_internal_leakage": no_internal_leakage,
        "no_unapproved_evolution": no_unapproved_evolution,
        "no_false_perfection": no_false_perfection,
        "leaked_names": leaked_names,
        "blocked_by": blocked_by,
    }


def load_premium_agent_standard() -> Dict[str, Any]:
    return deepcopy(PREMIUM_AGENT_STANDARD)
