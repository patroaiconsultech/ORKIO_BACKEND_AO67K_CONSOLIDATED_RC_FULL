from __future__ import annotations

import json
import logging
from typing import Any, Dict

OEP_001_TELEMETRY_VERSION = "OEP_001_EVOLUTION_TELEMETRY_V1"
logger = logging.getLogger("orkio.evolution")

def emit_evolution_event(event: str, payload: Dict[str, Any]) -> None:
    record = {"version": OEP_001_TELEMETRY_VERSION, "event": event, "payload": payload or {}}
    try:
        logger.info("OEP001_EVOLUTION_EVENT %s", json.dumps(record, ensure_ascii=False, sort_keys=True))
    except Exception:
        pass
