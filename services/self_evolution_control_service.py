from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, Optional


WRITE_SCOPES = {
    "write_file",
    "write_branch",
    "open_pr",
    "merge",
    "migration",
    "deploy",
    "runtime_patch",
    "frontend_patch",
    "backend_patch",
}

READONLY_SCOPES = {
    "readonly_audit",
    "diagnosis",
    "plan",
    "proposal",
    "test_matrix",
    "report",
}


def _text(value: Any) -> str:
    return str(value or "").strip()


def _lower(value: Any) -> str:
    return _text(value).lower()


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    text_l = _lower(text)
    return any(_lower(term) in text_l for term in terms if _text(term))


def evaluate_self_evolution_control(
    *,
    action_scope: str,
    requested_by: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Founder-controlled self-evolution gate.

    Default is readonly. Any write, branch, PR, merge, migration or deploy must
    be explicitly authorized by Daniel in the surrounding governance context.

    This module is side-effect free:
    - no writes
    - no network
    - no database
    - no deploy
    """

    context = deepcopy(context or {})
    scope = _lower(action_scope)
    requested_by_l = _lower(requested_by)

    founder_authorization_present = bool(
        context.get("founder_authorization_present")
        or context.get("explicit_founder_authorization")
        or context.get("daniel_approved")
    )

    is_write = scope in WRITE_SCOPES or _contains_any(scope, WRITE_SCOPES)
    is_readonly = scope in READONLY_SCOPES or _contains_any(scope, READONLY_SCOPES)

    blocked_by = []
    if is_write and not founder_authorization_present:
        blocked_by.append("founder_authorization_required")
    if _contains_any(_lower(context.get("message")), ["sem autorização", "ignore policy", "ignore a política"]):
        blocked_by.append("policy_bypass_attempt")

    allowed = not blocked_by and (is_readonly or founder_authorization_present or not is_write)
    mode = "write_authorized" if is_write and allowed else "readonly"

    return {
        "version": "AO67G-v1",
        "allowed": allowed,
        "mode": mode,
        "action_scope": action_scope,
        "requested_by": requested_by or "",
        "is_write_scope": is_write,
        "is_readonly_scope": is_readonly,
        "founder_authorization_present": founder_authorization_present,
        "controlled_by": "Daniel Graebin",
        "must_generate_audit_receipt": True,
        "must_support_rollback": bool(is_write),
        "blocked_by": blocked_by,
        "reason": (
            "ação permitida dentro da governança de autoevolução"
            if allowed
            else "ação bloqueada por governança de autoevolução: " + ", ".join(blocked_by)
        ),
    }
