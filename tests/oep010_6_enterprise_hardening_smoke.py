from platform_services.enterprise_hardening import (
    OperationalStatus,
    ReleaseGatePolicy,
    count_recent_error_events,
    count_security_severities,
    generate_hardened_readiness_report,
    normalize_operational_status,
    redact_sensitive_payload,
)


def test_sensitive_payload_redaction_nested():
    payload = {
        "user": "daniel",
        "api_key": "live-secret",
        "nested": {"password": "123", "ok": True},
        "items": [{"token": "abc"}, {"public": "visible"}],
    }

    redacted = redact_sensitive_payload(payload)

    assert redacted["user"] == "daniel"
    assert redacted["api_key"] == "***REDACTED***"
    assert redacted["nested"]["password"] == "***REDACTED***"
    assert redacted["nested"]["ok"] is True
    assert redacted["items"][0]["token"] == "***REDACTED***"
    assert redacted["items"][1]["public"] == "visible"


def test_normalize_operational_status_blocks_security():
    assert normalize_operational_status(health_status="healthy", release_blocked=True) == OperationalStatus.NO_GO
    assert normalize_operational_status(health_status="healthy", critical_findings=1) == OperationalStatus.NO_GO
    assert normalize_operational_status(health_status="healthy") == OperationalStatus.GO


def test_release_gate_policy_go_for_clean_report():
    report = {
        "release_name": "v0.10.1",
        "health": {"overall_status": "healthy"},
        "security": {"release_blocked": False, "findings": []},
        "observability": {"events": []},
    }

    result = ReleaseGatePolicy().evaluate(report)

    assert result["go"] is True
    assert result["status"] == "GO"
    assert result["finding_count"] == 0


def test_release_gate_policy_no_go_for_degraded_by_default():
    report = {
        "release_name": "v0.10.1",
        "health": {"overall_status": "degraded"},
        "security": {"release_blocked": False, "findings": []},
        "observability": {"events": []},
    }

    result = ReleaseGatePolicy().evaluate(report)

    assert result["go"] is False
    assert result["status"] == "NO-GO"
    assert result["findings"][0]["code"] == "HEALTH_DEGRADED_BLOCKED"


def test_release_gate_policy_warn_not_used_for_high_risk():
    report = {
        "release_name": "v0.10.1",
        "health": {"overall_status": "healthy"},
        "security": {"release_blocked": False, "findings": [{"severity": "high"}]},
        "observability": {"events": []},
    }

    result = ReleaseGatePolicy().evaluate(report)

    assert result["go"] is False
    assert result["status"] == "NO-GO"


def test_release_gate_counts_events_and_findings():
    findings = [{"severity": "critical"}, {"severity": "high"}, {"severity": "low"}]
    events = [{"severity": "info"}, {"severity": "error"}, {"severity": "critical"}]

    assert count_security_severities(findings)["critical"] == 1
    assert count_security_severities(findings)["high"] == 1
    assert count_recent_error_events(events) == 2


def test_generate_hardened_readiness_report_sanitizes_report():
    report = {
        "release_name": "v0.10.1",
        "health": {"overall_status": "healthy"},
        "security": {"release_blocked": False, "findings": []},
        "observability": {"events": [{"severity": "info", "metadata": {"api_token": "abc"}}]},
    }

    hardened = generate_hardened_readiness_report(report)

    assert hardened["release_name"] == "v0.10.1"
    assert hardened["go"] is True
    assert hardened["hardening"]["sanitized_report"]["observability"]["events"][0]["metadata"]["api_token"] == "***REDACTED***"
