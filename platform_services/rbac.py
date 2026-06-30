from __future__ import annotations
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "owner": {"*"},
    "admin": {"organization:read", "workspace:write", "project:write", "proposal:approve", "audit:read"},
    "manager": {"organization:read", "workspace:read", "project:write", "proposal:approve", "audit:read"},
    "editor": {"organization:read", "workspace:read", "project:write", "proposal:create"},
    "reviewer": {"organization:read", "workspace:read", "project:read", "proposal:approve", "audit:read"},
    "viewer": {"organization:read", "workspace:read", "project:read", "audit:read"},
}

class RBACService:
    def __init__(self) -> None:
        self._assignments: dict[tuple[str, str], str] = {}
    def assign_role(self, organization_id: str, user_id: str, role: str) -> dict:
        if role not in ROLE_PERMISSIONS:
            raise ValueError(f"unknown role: {role}")
        self._assignments[(organization_id, user_id)] = role
        return {"organization_id": organization_id, "user_id": user_id, "role": role}
    def get_role(self, organization_id: str, user_id: str) -> str | None:
        return self._assignments.get((organization_id, user_id))
    def can(self, organization_id: str, user_id: str, permission: str) -> bool:
        role = self.get_role(organization_id, user_id)
        if role is None:
            return False
        permissions = ROLE_PERMISSIONS[role]
        return "*" in permissions or permission in permissions

rbac_service = RBACService()
