#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

from knowledge_fabric.google_drive.connector import list_drive_inventory
from knowledge_fabric.google_drive.inventory import build_inventory_report, write_inventory_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ORKIO Knowledge Fabric — Google Drive metadata inventory only."
    )
    parser.add_argument("--folder-id", default=os.getenv("ORKIO_KF_DRIVE_FOLDER_ID"))
    parser.add_argument("--output", default="knowledge_fabric_out/drive_inventory.json")
    parser.add_argument("--page-size", type=int, default=100)
    args = parser.parse_args()

    if not args.folder_id:
        raise SystemExit("Missing --folder-id or ORKIO_KF_DRIVE_FOLDER_ID")

    items = list_drive_inventory(
        args.folder_id,
        mode="inventory_only",
        page_size=args.page_size,
    )
    report = build_inventory_report(items)
    out = write_inventory_report(report, args.output)

    print(f"ORKIO_KF_DRIVE_INVENTORY_OK items={len(items)} output={out}")
    print("runtime_use_allowed=false requires_human_approval=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
