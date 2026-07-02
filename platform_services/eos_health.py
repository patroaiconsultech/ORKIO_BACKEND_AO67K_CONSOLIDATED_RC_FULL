from __future__ import annotations

import os
import time
from typing import Any, Dict


def _env(name: str, default: str = "") -> str:
    return str(os.getenv(name, default) or default).strip()


def get_eos_health_snapshot(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Lightweight EOS health snapshot.

    This module is intentionally dependency-light so it can be imported during
    early FastAPI bootstrap without breaking production startup.
    """
    return {
        "status": "ok",
        "service": "orkio-eos",
        "module": "platform_services.eos_health",
        "timestamp": int(time.time()),
        "environment": _env("APP_ENV", "production"),
        "version": _env("APP_VERSION", "2.4.0"),
        "checks": {
            "bootstrap": "ok",
            "platform_services": "ok",
            "eos_health": "ok",
        },
        "capabilities": {
            "health_snapshot": True,
            "readiness_summary": True,
            "safe_bootstrap": True,
        },
    }
