#!/usr/bin/env python3
from pathlib import Path
import sys, json, re

ROOT = Path(__file__).resolve().parents[3]
PKG = ROOT / "specification" / "packages" / "OES-RC-0005-R4"
SPEC = ROOT / "specification" / "OES-008_FOUNDER_CONTEXT_TRIAGE_USAGE_GOVERNANCE.md"
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".py"}
FORBIDDEN_PATH_PARTS = {"private_raw", "raw_export", "account_export", "chatgpt_export", "gdrive_raw", "drive_raw", "memory_dump", "conversation_dump", "credential_dump"}
FORBIDDEN_FIELD_NAMES = {"raw_content", "source_content", "conversation_text", "message_text", "export_payload", "private_link", "credential", "token", "secret", "password"}
ALLOWED_CONTROL_FIELD_NAMES = {"raw_content_included", "raw_content_allowed"}

SENSITIVE_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "private_drive_url": re.compile(r"https?://(?:docs|drive)\.google\.com/[^\s)]+", re.I),
    "openai_export_file": re.compile(r"\b(conversations\.json|message\.json|user\.json)\b", re.I),
    "api_key_like": re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "cpf_like": re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
}

def iter_text_files():
    yield SPEC
    for path in PKG.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            yield path

def walk_json_values(data, path="$"):
    if isinstance(data, dict):
        for k, v in data.items():
            yield (path + "." + str(k), k, v)
            yield from walk_json_values(v, path + "." + str(k))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            yield from walk_json_values(v, f"{path}[{i}]")

def main() -> int:
    errors = []
    for path in iter_text_files():
        if not path.exists():
            errors.append(f"Missing expected text file: {path.relative_to(ROOT)}")
            continue
        rel = path.relative_to(ROOT)
        parts = {p.lower() for p in rel.parts}
        if parts & FORBIDDEN_PATH_PARTS:
            errors.append(f"Forbidden raw-content path: {rel}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"Non UTF-8 text file: {rel}")
            continue
        for name, pattern in SENSITIVE_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"Sensitive pattern {name} found in {rel}")
        if path.suffix.lower() == ".json":
            try:
                data = json.loads(text)
            except Exception as exc:
                errors.append(f"Invalid JSON: {rel}: {exc}")
                continue
            for json_path, key, value in walk_json_values(data):
                if isinstance(key, str):
                    key_l = key.lower()
                    if key_l in FORBIDDEN_FIELD_NAMES and key_l not in ALLOWED_CONTROL_FIELD_NAMES:
                        errors.append(f"Forbidden field name {key} in {rel} at {json_path}")
                if isinstance(value, str):
                    for name, pattern in SENSITIVE_PATTERNS.items():
                        if pattern.search(value):
                            errors.append(f"Sensitive pattern {name} in JSON value {rel} at {json_path}")
    register = json.loads((PKG / "private_source_register_seed.json").read_text(encoding="utf-8"))
    for source in register.get("sources", []):
        sid = source.get("source_id")
        if source.get("raw_content_included") is not False:
            errors.append(f"{sid}: raw_content_included must be false")
        if source.get("direct_publication_allowed") is not False:
            errors.append(f"{sid}: direct_publication_allowed must be false")
        if source.get("content_access_allowed") is not False:
            errors.append(f"{sid}: content_access_allowed must be false")
        if source.get("allowed_current_use") not in {"none", "metadata_only_without_content_access"}:
            errors.append(f"{sid}: allowed_current_use is not safe")
    learning = json.loads((PKG / "learning_signals_policy.json").read_text(encoding="utf-8"))
    if learning.get("raw_private_content_allowed") is not False:
        errors.append("Learning signals must forbid raw private content.")
    if errors:
        print("privacy_boundary_check: FAIL")
        for err in errors:
            print(err)
        return 1
    print("privacy_boundary_check: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
