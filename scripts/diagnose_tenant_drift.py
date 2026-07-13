#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from sqlalchemy import create_engine, text

from services.tenant_inventory_service import collect_tenant_inventory


def _database_url() -> str:
    value = (
        os.getenv("DATABASE_URL", "").strip()
        or os.getenv("DATABASE_PUBLIC_URL", "").strip()
        or os.getenv("DATABASE_URL_PUBLIC", "").strip()
    ).strip('"').strip("'")
    if value.startswith("postgres://"):
        value = "postgresql://" + value[len("postgres://") :]
    if not value:
        raise RuntimeError(
            "DATABASE_PUBLIC_URL, DATABASE_URL_PUBLIC or DATABASE_URL is required."
        )
    return value


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Collect a redacted, read-only tenant inventory for OEC005. "
            "No application modules are imported and no write is executed."
        )
    )
    parser.add_argument(
        "--email",
        action="append",
        default=[],
        help="Target account email. Repeat for tester/admin. Output is SHA-256 redacted.",
    )
    parser.add_argument(
        "--current-tenant",
        default=os.getenv("DEFAULT_TENANT", "public"),
        help="Tenant currently used by the frontend/session. Default: DEFAULT_TENANT or public.",
    )
    parser.add_argument(
        "--output",
        default="oec005_tenant_inventory.json",
        help="Path for the redacted JSON report.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    engine = create_engine(
        _database_url(),
        pool_pre_ping=True,
        pool_reset_on_return="rollback",
    )

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(text("SET TRANSACTION READ ONLY"))
            transaction_read_only = connection.execute(
                text("SELECT current_setting('transaction_read_only')")
            ).scalar_one()
            if str(transaction_read_only).strip().lower() not in {"on", "true"}:
                raise RuntimeError(
                    "OEC005 refused: transaction is not read-only"
                )

            report = collect_tenant_inventory(
                connection,
                target_emails=args.email,
                current_tenant=args.current_tenant,
            )
        finally:
            transaction.rollback()

    output_path = Path(args.output)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "status": "completed",
                "mode": "read_only",
                "output": str(output_path),
                "verdict": report["assessment"]["verdict"],
                "findings": len(report["assessment"]["findings"]),
                "write_executed": False,
                "migration_executed": False,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
