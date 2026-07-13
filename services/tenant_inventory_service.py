from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Iterable, Mapping, Protocol, Sequence

from sqlalchemy import text


class ReadOnlyConnection(Protocol):
    def execute(self, statement: Any, parameters: Mapping[str, Any] | None = None) -> Any:
        ...


@dataclass(frozen=True)
class TargetAccount:
    email_ref: str
    found: bool
    user_ref: str | None
    org_slug: str | None
    role: str | None
    approved: bool | None
    usage_tier: str | None


def normalize_email(value: str) -> str:
    return str(value or "").strip().lower()


def email_reference(value: str) -> str:
    normalized = normalize_email(value)
    if not normalized:
        return "email_sha256:missing"
    return f"email_sha256:{sha256(normalized.encode('utf-8')).hexdigest()[:12]}"


def identifier_reference(prefix: str, value: Any) -> str | None:
    normalized = str(value or "").strip()
    if not normalized:
        return None
    digest = sha256(normalized.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_sha256:{digest}"


def _rows_as_dicts(result: Any) -> list[dict[str, Any]]:
    mappings = getattr(result, "mappings", None)
    if callable(mappings):
        return [dict(row) for row in mappings().all()]
    rows = getattr(result, "all", None)
    if callable(rows):
        return [dict(row) if isinstance(row, Mapping) else dict(row._mapping) for row in rows()]
    return []


def _scalar_int(connection: ReadOnlyConnection, sql: str) -> int:
    result = connection.execute(text(sql))
    scalar = getattr(result, "scalar_one", None)
    if callable(scalar):
        return int(scalar() or 0)
    scalar = getattr(result, "scalar", None)
    if callable(scalar):
        return int(scalar() or 0)
    return 0


def _group_counts(connection: ReadOnlyConnection, table_name: str) -> dict[str, int]:
    allowed = {"users", "threads", "messages", "thread_members"}
    if table_name not in allowed:
        raise ValueError(f"Unsupported inventory table: {table_name}")

    result = connection.execute(
        text(
            f"""
            SELECT COALESCE(NULLIF(TRIM(org_slug), ''), '<missing>') AS org_slug,
                   COUNT(*)::BIGINT AS record_count
            FROM {table_name}
            GROUP BY COALESCE(NULLIF(TRIM(org_slug), ''), '<missing>')
            ORDER BY record_count DESC, org_slug
            """
        )
    )
    return {
        str(row["org_slug"]): int(row["record_count"])
        for row in _rows_as_dicts(result)
    }


def lookup_target_accounts(
    connection: ReadOnlyConnection,
    emails: Iterable[str],
) -> list[TargetAccount]:
    accounts: list[TargetAccount] = []

    for raw_email in emails:
        normalized = normalize_email(raw_email)
        if not normalized:
            continue

        result = connection.execute(
            text(
                """
                SELECT id,
                       org_slug,
                       role,
                       approved_at,
                       usage_tier
                FROM users
                WHERE LOWER(email) = :email
                ORDER BY org_slug, id
                """
            ),
            {"email": normalized},
        )
        rows = _rows_as_dicts(result)

        if not rows:
            accounts.append(
                TargetAccount(
                    email_ref=email_reference(normalized),
                    found=False,
                    user_ref=None,
                    org_slug=None,
                    role=None,
                    approved=None,
                    usage_tier=None,
                )
            )
            continue

        for row in rows:
            accounts.append(
                TargetAccount(
                    email_ref=email_reference(normalized),
                    found=True,
                    user_ref=identifier_reference("user", row.get("id")),
                    org_slug=str(row.get("org_slug")) if row.get("org_slug") is not None else None,
                    role=str(row.get("role")) if row.get("role") is not None else None,
                    approved=row.get("approved_at") is not None,
                    usage_tier=(
                        str(row.get("usage_tier"))
                        if row.get("usage_tier") is not None
                        else None
                    ),
                )
            )

    return accounts


def collect_tenant_inventory(
    connection: ReadOnlyConnection,
    *,
    target_emails: Sequence[str] = (),
    current_tenant: str | None = None,
) -> dict[str, Any]:
    database_meta_rows = _rows_as_dicts(
        connection.execute(
            text(
                """
                SELECT current_database() AS database_name,
                       NOW() AT TIME ZONE 'UTC' AS inspected_at_utc,
                       current_setting('transaction_read_only') AS transaction_read_only
                """
            )
        )
    )
    database_meta = database_meta_rows[0] if database_meta_rows else {}

    counts_by_tenant = {
        table: _group_counts(connection, table)
        for table in ("users", "threads", "messages", "thread_members")
    }

    consistency = {
        "thread_message_tenant_mismatches": _scalar_int(
            connection,
            """
            SELECT COUNT(*)
            FROM messages m
            JOIN threads t ON t.id = m.thread_id
            WHERE m.org_slug IS DISTINCT FROM t.org_slug
            """,
        ),
        "membership_thread_tenant_mismatches": _scalar_int(
            connection,
            """
            SELECT COUNT(*)
            FROM thread_members tm
            JOIN threads t ON t.id = tm.thread_id
            WHERE tm.org_slug IS DISTINCT FROM t.org_slug
            """,
        ),
        "message_user_tenant_mismatches": _scalar_int(
            connection,
            """
            SELECT COUNT(*)
            FROM messages m
            JOIN users u ON u.id = m.user_id
            WHERE m.user_id IS NOT NULL
              AND m.org_slug IS DISTINCT FROM u.org_slug
            """,
        ),
        "orphan_thread_memberships": _scalar_int(
            connection,
            """
            SELECT COUNT(*)
            FROM thread_members tm
            LEFT JOIN threads t ON t.id = tm.thread_id
            LEFT JOIN users u ON u.id = tm.user_id
            WHERE t.id IS NULL OR u.id IS NULL
            """,
        ),
        "duplicate_email_tenant_groups": _scalar_int(
            connection,
            """
            SELECT COUNT(*)
            FROM (
                SELECT LOWER(email)
                FROM users
                GROUP BY LOWER(email)
                HAVING COUNT(DISTINCT org_slug) > 1
            ) duplicated
            """,
        ),
    }

    target_accounts = [
        {
            "email_ref": item.email_ref,
            "found": item.found,
            "user_ref": item.user_ref,
            "org_slug": item.org_slug,
            "role": item.role,
            "approved": item.approved,
            "usage_tier": item.usage_tier,
        }
        for item in lookup_target_accounts(connection, target_emails)
    ]

    report: dict[str, Any] = {
        "mode": "read_only",
        "current_tenant": (current_tenant or "").strip() or None,
        "database": database_meta,
        "counts_by_tenant": counts_by_tenant,
        "target_accounts": target_accounts,
        "consistency": consistency,
    }
    report["assessment"] = assess_tenant_inventory(report)
    return report


def assess_tenant_inventory(report: Mapping[str, Any]) -> dict[str, Any]:
    current_tenant = str(report.get("current_tenant") or "").strip()
    counts = report.get("counts_by_tenant") or {}
    threads_by_tenant = counts.get("threads") or {}
    messages_by_tenant = counts.get("messages") or {}
    accounts = report.get("target_accounts") or []
    consistency = report.get("consistency") or {}

    findings: list[dict[str, str]] = []

    if current_tenant:
        current_threads = int(threads_by_tenant.get(current_tenant, 0) or 0)
        other_threads = sum(
            int(count or 0)
            for tenant, count in threads_by_tenant.items()
            if tenant != current_tenant
        )
        if current_threads == 0 and other_threads > 0:
            findings.append(
                {
                    "severity": "high",
                    "code": "CURRENT_TENANT_HAS_NO_THREADS",
                    "detail": (
                        "The current tenant has no threads while other tenants contain threads. "
                        "This is strong evidence of tenant visibility drift."
                    ),
                }
            )

        current_messages = int(messages_by_tenant.get(current_tenant, 0) or 0)
        other_messages = sum(
            int(count or 0)
            for tenant, count in messages_by_tenant.items()
            if tenant != current_tenant
        )
        if current_messages == 0 and other_messages > 0:
            findings.append(
                {
                    "severity": "high",
                    "code": "CURRENT_TENANT_HAS_NO_MESSAGES",
                    "detail": (
                        "The current tenant has no messages while other tenants contain messages."
                    ),
                }
            )

    for account in accounts:
        if not account.get("found"):
            findings.append(
                {
                    "severity": "high",
                    "code": "TARGET_ACCOUNT_NOT_FOUND",
                    "detail": f"{account.get('email_ref')} was not found in any tenant.",
                }
            )
            continue
        if current_tenant and account.get("org_slug") != current_tenant:
            findings.append(
                {
                    "severity": "high",
                    "code": "TARGET_ACCOUNT_TENANT_MISMATCH",
                    "detail": (
                        f"{account.get('email_ref')} belongs to tenant "
                        f"{account.get('org_slug')!r}, not {current_tenant!r}."
                    ),
                }
            )
        if account.get("approved") is False:
            findings.append(
                {
                    "severity": "medium",
                    "code": "TARGET_ACCOUNT_NOT_APPROVED",
                    "detail": f"{account.get('email_ref')} has no approved_at value.",
                }
            )

    for key, value in consistency.items():
        if int(value or 0) > 0:
            findings.append(
                {
                    "severity": "critical",
                    "code": key.upper(),
                    "detail": f"{key}={int(value)}",
                }
            )

    if not findings:
        verdict = "NO_TENANT_DRIFT_CONFIRMED"
    elif any(item["severity"] == "critical" for item in findings):
        verdict = "DATA_CONSISTENCY_RISK"
    elif any(item["severity"] == "high" for item in findings):
        verdict = "TENANT_DRIFT_LIKELY"
    else:
        verdict = "REVIEW_REQUIRED"

    return {
        "verdict": verdict,
        "findings": findings,
        "write_allowed": False,
        "migration_allowed": False,
        "recovery_allowed": False,
        "human_approval_required": True,
    }
