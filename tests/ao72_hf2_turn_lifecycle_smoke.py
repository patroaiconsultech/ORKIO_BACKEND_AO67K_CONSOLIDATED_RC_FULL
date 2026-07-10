from pathlib import Path

source = Path(__file__).resolve().parents[1] / "main.py"
text = source.read_text(encoding="utf-8")

required = [
    "AO72-HF2 — Turn-scoped Single Assistant Commit Guard.",
    'Message.client_message_id == _assistant_turn_key',
    'client_message_id=_assistant_turn_key',
    'AO72_HF2_TURN_COMMIT_GUARD',
    'AO72_HF2_CLIENT_DISCONNECTED_BACKGROUND_CONTINUES',
    '.filter(Message.client_message_id == assistant_turn_key)',
]

missing = [item for item in required if item not in text]
if missing:
    raise SystemExit(f"AO72_HF2_TURN_LIFECYCLE_SMOKE_FAIL missing={missing}")

forbidden = [
    'Message.content == _assistant_content,\n                        Message.created_at >= _recent_floor',
]

present = [item for item in forbidden if item in text]
if present:
    raise SystemExit(f"AO72_HF2_TURN_LIFECYCLE_SMOKE_FAIL legacy_guard_present={present}")

print("AO72_HF2_TURN_LIFECYCLE_SMOKE_PASS")
