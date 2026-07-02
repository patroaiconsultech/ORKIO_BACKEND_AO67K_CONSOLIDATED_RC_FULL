from __future__ import annotations

import os
from typing import Iterable, List, Optional

from .models import DriveInventoryItem
from .policy import enforce_policy


DEFAULT_FIELDS = (
    "nextPageToken, files("
    "id,name,mimeType,webViewLink,parents,size,createdTime,modifiedTime,md5Checksum"
    ")"
)


def _load_google_client():
    """Load Google Drive client lazily so the app can boot without Google deps."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Google Drive dependencies are missing. Install "
            "google-api-python-client and google-auth."
        ) from exc

    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is not configured.")

    scopes = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=scopes,
    )
    return build("drive", "v3", credentials=credentials, cache_discovery=False)


def list_drive_inventory(
    folder_id: str,
    *,
    mode: str = "inventory_only",
    page_size: int = 100,
    include_trashed: bool = False,
) -> List[DriveInventoryItem]:
    """List metadata-only inventory for one folder.

    This function intentionally does not download or read document content.
    """
    enforce_policy(mode)

    if not folder_id:
        raise ValueError("folder_id is required")

    service = _load_google_client()
    query = f"'{folder_id}' in parents"
    if not include_trashed:
        query += " and trashed = false"

    items: List[DriveInventoryItem] = []
    page_token: Optional[str] = None

    while True:
        response = (
            service.files()
            .list(
                q=query,
                fields=DEFAULT_FIELDS,
                pageSize=page_size,
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )

        for f in response.get("files", []):
            parents = f.get("parents") or []
            items.append(
                DriveInventoryItem(
                    drive_file_id=f.get("id", ""),
                    name=f.get("name", ""),
                    mime_type=f.get("mimeType", ""),
                    web_view_link=f.get("webViewLink"),
                    parent_folder_id=parents[0] if parents else folder_id,
                    size=f.get("size"),
                    created_time=f.get("createdTime"),
                    modified_time=f.get("modifiedTime"),
                    md5_checksum=f.get("md5Checksum"),
                )
            )

        page_token = response.get("nextPageToken")
        if not page_token:
            break

    return items
