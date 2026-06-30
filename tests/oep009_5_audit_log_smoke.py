from platform_services import OrganizationService, AuditLogService
org = OrganizationService().create("Audit Org")
audit = AuditLogService()
event = audit.record(
    organization_id=org["organization_id"],
    actor_id="user_1",
    action="proposal.approved",
    resource_type="proposal",
    resource_id="proposal_1",
)
events = audit.list_by_organization(org["organization_id"])
assert event["event_id"].startswith("evt_")
assert len(events) == 1
assert events[0]["action"] == "proposal.approved"
assert events[0]["proposal_only"] is True
assert events[0]["write_executed"] is False
assert events[0]["human_approval_required"] is True
print("OEP009_5_AUDIT_LOG_PASS")
