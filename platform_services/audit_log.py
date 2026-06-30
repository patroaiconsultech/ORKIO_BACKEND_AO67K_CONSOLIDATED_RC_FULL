from __future__ import annotations
from platform_services.models import AuditEvent, new_id

class AuditLogService:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
    def record(self, organization_id: str, actor_id: str, action: str, resource_type: str, resource_id: str, metadata: dict | None = None) -> dict:
        event = AuditEvent(
            event_id=new_id("evt"),
            organization_id=organization_id,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata or {},
        )
        self._events.append(event)
        return event.to_dict()
    def list_by_organization(self, organization_id: str) -> list[dict]:
        return [item.to_dict() for item in self._events if item.organization_id == organization_id]

audit_log_service = AuditLogService()
