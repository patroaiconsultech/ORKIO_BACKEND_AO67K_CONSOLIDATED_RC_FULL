from platform_services import OrganizationService, WorkspaceService, ProjectService
org = OrganizationService().create("Orkio Org")
workspace = WorkspaceService().create(org["organization_id"], "Main")
service = ProjectService()
project = service.create(org["organization_id"], workspace["workspace_id"], "Growth Diagnostic")
assert project["project_id"].startswith("prj_")
assert project["organization_id"] == org["organization_id"]
assert project["workspace_id"] == workspace["workspace_id"]
assert "knowledge" in project["modules"]
assert "governance" in project["modules"]
print("OEP009_3_PROJECT_SERVICE_PASS")
