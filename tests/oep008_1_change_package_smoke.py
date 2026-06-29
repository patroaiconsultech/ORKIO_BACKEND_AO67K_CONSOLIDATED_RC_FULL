from evolution.governed_evolution import ChangePackageBuilder
package=ChangePackageBuilder().build(title="Create governed change package",summary="Package must be auditable and reversible.",affected_modules=["evolution/governed_evolution/change_package.py"],proposal_id="prop_001")
data=package.to_dict()
assert data["package_id"].startswith("chg_")
assert data["proposal_only"] is True
assert data["write_executed"] is False
assert data["human_approval_required"] is True
assert data["rollback_plan"]["steps"]
assert data["validation_plan"]
print("OEP008_1_CHANGE_PACKAGE_PASS")
