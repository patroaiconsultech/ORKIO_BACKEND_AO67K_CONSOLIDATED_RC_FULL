from platform_services import OrganizationService, WorkspaceService
org = OrganizationService().create("PatroAI")
service = WorkspaceService()
workspace = service.create(org["organization_id"], "Summit Workspace", members=["daniel@patroai.com"])
assert workspace["workspace_id"].startswith("wks_")
assert workspace["organization_id"] == org["organization_id"]
assert workspace["knowledge_scope"] == "workspace"
assert len(service.list_by_organization(org["organization_id"])) == 1
print("OEP009_2_WORKSPACE_SERVICE_PASS")
