from platform_services.security_audit import SecurityAuditService, run_default_security_audit


def test_default_governance_is_not_blocked():
    summary = run_default_security_audit()
    assert summary["release_blocked"] is False
    assert summary["total"] == 0


def test_governance_mismatch_blocks_release():
    service = SecurityAuditService()
    findings = service.audit_governance_flags(
        {
            "proposal_only": False,
            "write_executed": True,
            "human_approval_required": False,
        }
    )
    summary = service.summarize(findings)
    assert summary["release_blocked"] is True
    assert summary["total"] == 3


def test_secret_exposure_is_critical():
    service = SecurityAuditService()
    findings = service.audit_secret_exposure({"OPENAI_API_KEY": "secret-value"})
    summary = service.summarize(findings)
    assert summary["max_severity"] == "critical"
    assert summary["release_blocked"] is True


if __name__ == "__main__":
    test_default_governance_is_not_blocked()
    test_governance_mismatch_blocks_release()
    test_secret_exposure_is_critical()
    print("OEP010_4_SECURITY_AUDIT_SMOKE_PASS")
