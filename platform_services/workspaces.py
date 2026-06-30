from __future__ import annotations
import re
from platform_services.models import Workspace, new_id

def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "workspace"

class WorkspaceService:
    def __init__(self) -> None:
        self._workspaces: dict[str, Workspace] = {}
    def create(self, organization_id: str, name: str, members: list[str] | None = None) -> dict:
        workspace = Workspace(
            workspace_id=new_id("wks"),
            organization_id=organization_id,
            name=name.strip(),
            slug=_slugify(name),
            members=members or [],
        )
        self._workspaces[workspace.workspace_id] = workspace
        return workspace.to_dict()
    def list_by_organization(self, organization_id: str) -> list[dict]:
        return [item.to_dict() for item in self._workspaces.values() if item.organization_id == organization_id]
    def get(self, workspace_id: str) -> dict:
        return self._workspaces[workspace_id].to_dict()

workspace_service = WorkspaceService()
