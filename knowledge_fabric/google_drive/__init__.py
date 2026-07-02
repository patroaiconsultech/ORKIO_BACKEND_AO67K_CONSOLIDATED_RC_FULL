"""
Google Drive connector for ORKIO Knowledge Fabric.

Default mode: inventory_only.
This package must not inject documents into Orkio runtime without approval.
"""
from .policy import DEFAULT_POLICY
from .models import DriveInventoryItem, ClassificationResult
from .classifier import classify_drive_item

__all__ = [
    "DEFAULT_POLICY",
    "DriveInventoryItem",
    "ClassificationResult",
    "classify_drive_item",
]
