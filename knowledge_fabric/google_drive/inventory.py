from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .classifier import classify_drive_item
from .models import DriveInventoryItem


def build_inventory_report(items: Iterable[DriveInventoryItem]) -> dict:
    rows = []
    classifications = []

    for item in items:
        rows.append(item.to_dict())
        classifications.append(classify_drive_item(item).to_dict())

    return {
        "policy": {
            "mode": "inventory_only",
            "runtime_use_allowed": False,
            "requires_human_approval": True,
        },
        "summary": {
            "total_items": len(rows),
        },
        "items": rows,
        "classifications": classifications,
    }


def write_inventory_report(report: dict, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
