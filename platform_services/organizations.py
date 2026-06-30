from __future__ import annotations
import re
from platform_services.models import Organization, new_id

def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "organization"

class OrganizationService:
    def __init__(self) -> None:
        self._organizations: dict[str, Organization] = {}
    def create(self, name: str, plan: str = "beta", settings: dict | None = None) -> dict:
        organization = Organization(
            organization_id=new_id("org"),
            name=name.strip(),
            slug=_slugify(name),
            plan=plan,
            settings=settings or {},
        )
        self._organizations[organization.organization_id] = organization
        return organization.to_dict()
    def get(self, organization_id: str) -> dict:
        return self._organizations[organization_id].to_dict()
    def list(self) -> list[dict]:
        return [item.to_dict() for item in self._organizations.values()]
    def assert_isolated(self, left_org_id: str, right_org_id: str) -> bool:
        return bool(left_org_id and right_org_id and left_org_id != right_org_id)

organization_service = OrganizationService()
