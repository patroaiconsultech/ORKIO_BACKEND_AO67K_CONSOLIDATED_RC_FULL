-- OEC005 — Tenant/Auth/Thread Visibility Inventory
-- PostgreSQL only.
-- Safety contract: this file contains SELECT statements inside a READ ONLY transaction.
-- Do not add UPDATE, INSERT, DELETE, ALTER, CREATE, DROP or migration statements.

BEGIN TRANSACTION READ ONLY;

SELECT
    current_database() AS database_name,
    NOW() AT TIME ZONE 'UTC' AS inspected_at_utc,
    current_setting('transaction_read_only') AS transaction_read_only;

SELECT
    COALESCE(NULLIF(TRIM(org_slug), ''), '<missing>') AS org_slug,
    COUNT(*) AS users_count
FROM users
GROUP BY COALESCE(NULLIF(TRIM(org_slug), ''), '<missing>')
ORDER BY users_count DESC, org_slug;

SELECT
    COALESCE(NULLIF(TRIM(org_slug), ''), '<missing>') AS org_slug,
    COUNT(*) AS threads_count
FROM threads
GROUP BY COALESCE(NULLIF(TRIM(org_slug), ''), '<missing>')
ORDER BY threads_count DESC, org_slug;

SELECT
    COALESCE(NULLIF(TRIM(org_slug), ''), '<missing>') AS org_slug,
    COUNT(*) AS messages_count
FROM messages
GROUP BY COALESCE(NULLIF(TRIM(org_slug), ''), '<missing>')
ORDER BY messages_count DESC, org_slug;

SELECT
    COALESCE(NULLIF(TRIM(org_slug), ''), '<missing>') AS org_slug,
    COUNT(*) AS memberships_count
FROM thread_members
GROUP BY COALESCE(NULLIF(TRIM(org_slug), ''), '<missing>')
ORDER BY memberships_count DESC, org_slug;

SELECT
    COUNT(*) AS thread_message_tenant_mismatches
FROM messages m
JOIN threads t ON t.id = m.thread_id
WHERE m.org_slug IS DISTINCT FROM t.org_slug;

SELECT
    COUNT(*) AS membership_thread_tenant_mismatches
FROM thread_members tm
JOIN threads t ON t.id = tm.thread_id
WHERE tm.org_slug IS DISTINCT FROM t.org_slug;

SELECT
    COUNT(*) AS message_user_tenant_mismatches
FROM messages m
JOIN users u ON u.id = m.user_id
WHERE m.user_id IS NOT NULL
  AND m.org_slug IS DISTINCT FROM u.org_slug;

SELECT
    COUNT(*) AS orphan_thread_memberships
FROM thread_members tm
LEFT JOIN threads t ON t.id = tm.thread_id
LEFT JOIN users u ON u.id = tm.user_id
WHERE t.id IS NULL OR u.id IS NULL;

-- Target accounts must be checked separately with bound parameters through
-- scripts/diagnose_tenant_drift.py. Do not paste passwords, tokens or hashes here.

ROLLBACK;
