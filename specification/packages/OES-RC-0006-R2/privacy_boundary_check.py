#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
MANIFEST = PACKAGE / "OES-RC-0006-R2_MANIFEST_SHA256.txt"

TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".py"}

# Build sensitive markers without embedding the full forbidden phrases as contiguous source text.
CHATGPT_EXPORT = "chatgpt" + r"\s+" + "export"
CONVERSATION_JSON = "conversation" + r"\.json"
MESSAGE_JSON = "message" + r"\.json"
RAW_PRIVATE_CONTENT = "raw" + r"\s+" + "private" + r"\s+" + "content"

PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "google_drive_link": re.compile(r"https?://(?:drive|docs)\.google\.com/[^\s)]+", re.I),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
    "api_token": re.compile(r"(?i)(api[_-]?key|secret|token|credential|password)\s*[:=]\s*[A-Za-z0-9_\-]{12,}"),
    "cpf_like": re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"),
    "raw_export_marker": re.compile(r"(?i)(" + CHATGPT_EXPORT + r"|" + CONVERSATION_JSON + r"|" + MESSAGE_JSON + r"|" + RAW_PRIVATE_CONTENT + r")")
}

def main() -> int:
    errors = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        _, rel = line.split("  ", 1)
        rel_posix = Path(rel.strip()).as_posix()
        p = ROOT / rel_posix
        if p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for label, pattern in PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{label}: {rel_posix}")
    if errors:
        print("privacy_boundary_check: FAIL")
        for e in errors:
            print(e)
        return 1
    print("privacy_boundary_check: PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
