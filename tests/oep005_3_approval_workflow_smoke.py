from evolution.proposal_engine.approval import ProposalApprovalWorkflow

workflow = ProposalApprovalWorkflow()
proposal = {"proposal_id": "p1", "title": "Governed proposal", "confidence": 0.91}

submitted = workflow.submit(proposal)
approved = workflow.approve(submitted, approved_by="human_reviewer")

assert submitted["status"] == "submitted"
assert approved["status"] == "approved"
assert approved["approved_by"] == "human_reviewer"
assert approved["proposal_only"] is True
assert approved["requires_human_approval"] is True
print("OEP005_3_APPROVAL_WORKFLOW_PASS")
