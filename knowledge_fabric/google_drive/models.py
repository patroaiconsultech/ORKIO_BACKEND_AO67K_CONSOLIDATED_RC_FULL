from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class DriveInventoryItem:
    """Metadata-only inventory item for a Google Drive file."""

    drive_file_id: str
    name: str
    mime_type: str
    web_view_link: Optional[str] = None
    parent_folder_id: Optional[str] = None
    size: Optional[str] = None
    created_time: Optional[str] = None
    modified_time: Optional[str] = None
    md5_checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClassificationResult:
    """Initial non-authoritative classification for review."""

    drive_file_id: str
    knowledge_class: str
    sensitivity: str
    status: str
    confidence: float
    reason: str
    runtime_use_allowed: bool = False
    requires_human_approval: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
