from platform_services import OrganizationService, RBACService
org = OrganizationService().create("RBAC Org")
rbac = RBACService()
assignment = rbac.assign_role(org["organization_id"], "user_1", "reviewer")
assert assignment["role"] == "reviewer"
assert rbac.can(org["organization_id"], "user_1", "proposal:approve") is True
assert rbac.can(org["organization_id"], "user_1", "project:write") is False
assert rbac.can(org["organization_id"], "unknown", "audit:read") is False
print("OEP009_4_RBAC_PASS")
