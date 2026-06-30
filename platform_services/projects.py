from __future__ import annotations
import re
from platform_services.models import Project, new_id

def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "project"

class ProjectService:
    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}
    def create(self, organization_id: str, workspace_id: str, name: str) -> dict:
        project = Project(
            project_id=new_id("prj"),
            organization_id=organization_id,
            workspace_id=workspace_id,
            name=name.strip(),
            slug=_slugify(name),
        )
        self._projects[project.project_id] = project
        return project.to_dict()
    def list_by_workspace(self, workspace_id: str) -> list[dict]:
        return [item.to_dict() for item in self._projects.values() if item.workspace_id == workspace_id]
    def get(self, project_id: str) -> dict:
        return self._projects[project_id].to_dict()

project_service = ProjectService()
