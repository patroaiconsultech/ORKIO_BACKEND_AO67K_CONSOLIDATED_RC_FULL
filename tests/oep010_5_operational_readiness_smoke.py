from platform_services.operational_readiness import generate_operational_readiness_report


def test_operational_readiness_go():
    report = generate_operational_readiness_report()
    assert report["status"] == "GO"
    assert report["go"] is True
    assert report["health"]["overall_status"] == "healthy"


def test_operational_readiness_no_go_when_governance_breaks():
    report = generate_operational_readiness_report(
        governance_flags={
            "proposal_only": False,
            "write_executed": True,
            "human_approval_required": False,
        }
    )
    assert report["status"] == "NO-GO"
    assert report["go"] is False
    assert report["security"]["release_blocked"] is True


if __name__ == "__main__":
    test_operational_readiness_go()
    test_operational_readiness_no_go_when_governance_breaks()
    print("OEP010_5_OPERATIONAL_READINESS_SMOKE_PASS")
