from services.tenant_inventory_service import (
    assess_tenant_inventory,
    email_reference,
    identifier_reference,
    normalize_email,
)


def test_normalize_email_is_stable():
    assert normalize_email("  Tester@Example.COM ") == "tester@example.com"


def test_email_reference_is_redacted_and_deterministic():
    first = email_reference("tester@example.com")
    second = email_reference(" TESTER@example.com ")
    assert first == second
    assert first.startswith("email_sha256:")
    assert "tester" not in first


def test_assessment_detects_current_tenant_without_threads():
    report = {
        "current_tenant": "public",
        "counts_by_tenant": {
            "threads": {"legacy": 12, "public": 0},
            "messages": {"legacy": 44, "public": 0},
        },
        "target_accounts": [],
        "consistency": {
            "thread_message_tenant_mismatches": 0,
            "membership_thread_tenant_mismatches": 0,
            "message_user_tenant_mismatches": 0,
            "orphan_thread_memberships": 0,
            "duplicate_email_tenant_groups": 0,
        },
    }
    assessment = assess_tenant_inventory(report)
    assert assessment["verdict"] == "TENANT_DRIFT_LIKELY"
    codes = {item["code"] for item in assessment["findings"]}
    assert "CURRENT_TENANT_HAS_NO_THREADS" in codes
    assert "CURRENT_TENANT_HAS_NO_MESSAGES" in codes


def test_assessment_detects_target_account_tenant_mismatch():
    report = {
        "current_tenant": "public",
        "counts_by_tenant": {
            "threads": {"public": 1},
            "messages": {"public": 1},
        },
        "target_accounts": [
            {
                "email_ref": "email_sha256:abc",
                "found": True,
                "org_slug": "legacy",
                "approved": True,
            }
        ],
        "consistency": {},
    }
    assessment = assess_tenant_inventory(report)
    assert assessment["verdict"] == "TENANT_DRIFT_LIKELY"
    assert any(
        item["code"] == "TARGET_ACCOUNT_TENANT_MISMATCH"
        for item in assessment["findings"]
    )


def test_assessment_blocks_recovery_when_consistency_is_broken():
    report = {
        "current_tenant": "public",
        "counts_by_tenant": {
            "threads": {"public": 1},
            "messages": {"public": 1},
        },
        "target_accounts": [],
        "consistency": {"thread_message_tenant_mismatches": 2},
    }
    assessment = assess_tenant_inventory(report)
    assert assessment["verdict"] == "DATA_CONSISTENCY_RISK"
    assert assessment["write_allowed"] is False
    assert assessment["recovery_allowed"] is False


def test_assessment_does_not_claim_drift_without_evidence():
    report = {
        "current_tenant": "public",
        "counts_by_tenant": {
            "threads": {"public": 4},
            "messages": {"public": 20},
        },
        "target_accounts": [
            {
                "email_ref": "email_sha256:abc",
                "found": True,
                "org_slug": "public",
                "approved": True,
            }
        ],
        "consistency": {
            "thread_message_tenant_mismatches": 0,
            "membership_thread_tenant_mismatches": 0,
            "message_user_tenant_mismatches": 0,
            "orphan_thread_memberships": 0,
            "duplicate_email_tenant_groups": 0,
        },
    }
    assessment = assess_tenant_inventory(report)
    assert assessment["verdict"] == "NO_TENANT_DRIFT_CONFIRMED"
    assert assessment["findings"] == []


def test_identifier_reference_redacts_internal_ids():
    ref = identifier_reference("user", "internal-user-id-123")
    assert ref is not None
    assert ref.startswith("user_sha256:")
    assert "internal-user-id-123" not in ref


def test_identifier_reference_handles_missing_values():
    assert identifier_reference("user", None) is None
    assert identifier_reference("user", "") is None
