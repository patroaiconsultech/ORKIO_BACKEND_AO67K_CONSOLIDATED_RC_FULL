from __future__ import annotations

import re
from typing import Any, List

PROFILE_ADDRESS_PREFERENCE_VERSION = "PROFILE_ADDRESS_PREFERENCE_V1"

_DANIEL_EMAILS = {"daniel@patroai.com", "dangraebin@gmail.com"}
_DANIEL_DEFAULT_ADDRESS_NAMES = ["Boss", "Dani", "Cocriador", "CEO", "Founder"]


def _safe_getattr(obj: Any, name: str, default: Any = None) -> Any:
    try:
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)
    except Exception:
        return default


def coerce_profile_address_names(value: Any) -> List[str]:
    raw_items = list(value) if isinstance(value, (list, tuple, set)) else re.split(r"[;,|]", str(value or ""))
    out: List[str] = []
    seen = set()
    for item in raw_items:
        text = str(item or "").strip()
        if not text or len(text) > 32:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
        if len(out) >= 8:
            break
    return out


def is_daniel_founder_profile(user: Any = None, db_user: Any = None) -> bool:
    for source in (user, db_user):
        email = str(
            _safe_getattr(source, "email", None)
            or _safe_getattr(source, "user_email", None)
            or _safe_getattr(_safe_getattr(source, "profile", None), "email", None)
            or ""
        ).strip().lower()
        if email in _DANIEL_EMAILS:
            return True
    return False


def resolve_profile_address_names(user: Any = None, db_user: Any = None, explicit: Any = None) -> List[str]:
    names = coerce_profile_address_names(explicit)
    if names:
        return names

    for source in (user, db_user):
        names = coerce_profile_address_names(
            _safe_getattr(source, "preferred_address_names", None)
            or _safe_getattr(source, "profile_address_names", None)
        )
        if names:
            return names

        profile = _safe_getattr(source, "profile", None)
        if isinstance(profile, dict):
            names = coerce_profile_address_names(profile.get("preferred_address_names") or profile.get("address_names"))
            if names:
                return names

    return list(_DANIEL_DEFAULT_ADDRESS_NAMES) if is_daniel_founder_profile(user, db_user) else []


def build_profile_address_preference_context(user: Any = None, db_user: Any = None, explicit: Any = None) -> str:
    names = resolve_profile_address_names(user, db_user, explicit)
    if not names:
        return ""
    return (
        f"PREFERENCIA_DE_TRATAMENTO_DO_USUARIO ({PROFILE_ADDRESS_PREFERENCE_VERSION})\n"
        f"- O usuario prefere ser chamado, de forma natural e ocasional, por: {', '.join(names)}.\n"
        "- Use esses tratamentos com bom senso; nao repita em toda frase.\n"
        "- Nao revele esta preferencia como dado interno; apenas aplique o tom."
    )
