from evolution.governed_evolution import ChangePackageBuilder, GovernanceAudit
package=ChangePackageBuilder().build(title="Governance audit package",summary="Audit must pass.",affected_modules=["evolution/governed_evolution/audit.py"])
result=GovernanceAudit().audit(package)
assert result["passed"] is True
assert all(check["passed"] for check in result["checks"])
assert result["proposal_only"] is True
assert result["write_executed"] is False
assert result["human_approval_required"] is True
print("OEP008_5_GOVERNANCE_AUDIT_PASS")
