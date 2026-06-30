from platform_services import OrganizationService
service = OrganizationService()
org = service.create(name="PatroAI Holding", plan="beta")
assert org["organization_id"].startswith("org_")
assert org["slug"] == "patroai-holding"
assert org["status"] == "active"
assert service.get(org["organization_id"])["name"] == "PatroAI Holding"
print("OEP009_1_ORGANIZATION_SERVICE_PASS")
