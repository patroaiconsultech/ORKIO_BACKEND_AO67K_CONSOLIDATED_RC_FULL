from evolution.governed_evolution import ApprovalPipeline, ChangePackageBuilder
package=ChangePackageBuilder().build(title="Approval package",summary="Human approval required.",affected_modules=["evolution/governed_evolution/approval.py"])
approved=ApprovalPipeline().approve(ApprovalPipeline().submit(package),approver="human:daniel",reason="Smoke approval")
data=approved.to_dict()
assert data["status"]=="approved"
assert len(data["approvals"])==1
assert data["approvals"][0]["decision"]=="approved"
assert data["proposal_only"] is True
assert data["write_executed"] is False
assert data["human_approval_required"] is True
print("OEP008_4_APPROVAL_PIPELINE_PASS")
