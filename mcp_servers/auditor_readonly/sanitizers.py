"""Sanitization helpers for logs, errors, refs and runtime values."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b", re.IGNORECASE)
COOKIE_RE = re.compile(r"\b(cookie|set-cookie)\s*[:=]\s*[^;\n\r]+", re.IGNORECASE)
PASSWORD_RE = re.compile(r"\b(password|passwd|pwd|senha)\s*[:=]\s*[^,\s}\]\n\r]+", re.IGNORECASE)
TOKEN_RE = re.compile(r"\b(token|access_token|refresh_token|id_token|api_key|apikey|secret)\s*[:=]\s*[^,\s}\]\n\r]+", re.IGNORECASE)
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
HEX_SECRET_RE = re.compile(r"\b[a-f0-9]{32,}\b", re.IGNORECASE)
QUERY_SECRET_KEYS = {"token", "access_token", "refresh_token", "id_token", "api_key", "apikey", "secret", "password", "senha", "cookie"}
SENSITIVE_DICT_KEYS = {"content", "body", "text", "raw_text", "extracted_text", "chunk_text", "embedding", "password", "token", "secret", "cookie"}


def sha256_short(value: str, length: int = 12) -> str:
    digest = hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()
    return digest[:length]


def hash_identifier(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    if not text:
        return None
    return f"sha256:{sha256_short(text)}"


def mask_email(match: re.Match[str]) -> str:
    email = match.group(0)
    local, _, domain = email.partition("@")
    domain_hash = sha256_short(domain.lower(), 8)
    local_hash = sha256_short(local.lower(), 8)
    return f"email:{local_hash}@domain:{domain_hash}"


def sanitize_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
    except ValueError:
        return value
    if not parsed.query:
        return value
    safe_query = []
    for key, val in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() in QUERY_SECRET_KEYS:
            safe_query.append((key, "[redacted]"))
        else:
            safe_query.append((key, val))
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(safe_query), parsed.fragment))


def sanitize_text(value: Any, max_chars: int = 2000) -> str:
    text = "" if value is None else str(value)
    text = EMAIL_RE.sub(mask_email, text)
    text = BEARER_RE.sub("Bearer [redacted]", text)
    text = COOKIE_RE.sub(lambda match: f"{match.group(1)}=[redacted]", text)
    text = PASSWORD_RE.sub(lambda match: f"{match.group(1)}=[redacted]", text)
    text = TOKEN_RE.sub(lambda match: f"{match.group(1)}=[redacted]", text)
    text = JWT_RE.sub("jwt:[redacted]", text)
    text = HEX_SECRET_RE.sub("hex:[redacted]", text)
    text = sanitize_url(text)
    if len(text) > max_chars:
        return text[:max_chars] + "...[truncated]"
    return text


def sanitize_filename(value: Any) -> dict[str, str | None]:
    if value is None:
        return {"filename_ref": None, "extension": None}
    path = Path(str(value))
    suffix = path.suffix.lower()[:16] if path.suffix else None
    stem = path.stem or str(value)
    return {"filename_ref": hash_identifier(stem), "extension": suffix}


def sanitize_mapping(value: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, item in value.items():
        key_text = str(key)
        if key_text.lower() in SENSITIVE_DICT_KEYS:
            sanitized[key_text] = "[redacted]"
        elif isinstance(item, str):
            sanitized[key_text] = sanitize_text(item)
        elif isinstance(item, dict):
            sanitized[key_text] = sanitize_mapping(item)
        elif isinstance(item, list):
            sanitized[key_text] = [sanitize_text(entry) if isinstance(entry, str) else entry for entry in item[:50]]
        else:
            sanitized[key_text] = item
    return sanitized


def safe_error(error: BaseException) -> dict[str, str]:
    return {
        "type": error.__class__.__name__,
        "message": sanitize_text(str(error), max_chars=400),
    }


def runtime_value_for_public_flag(name: str, value: str, allowlist: tuple[str, ...]) -> str:
    upper_name = name.upper()
    sensitive = any(part in upper_name for part in ("SECRET", "TOKEN", "PASSWORD", "PASS", "COOKIE", "KEY", "DATABASE_URL", "DSN"))
    if sensitive:
        return "[redacted]"
    if name in allowlist and value.lower() in {"true", "false", "1", "0", "yes", "no", "on", "off"}:
        return value.lower()
    if value == "":
        return "empty"
    return "set"
