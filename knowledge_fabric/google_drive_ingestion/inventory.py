from typing import Iterable, List, Dict, Any
from .models import KnowledgeItem

def inventory_stub(items: Iterable[Dict[str, Any]]) -> List[KnowledgeItem]:
    """Inventory-only helper. Does not fetch file contents."""
    result = []
    for raw in items:
        result.append(KnowledgeItem(
            source_id=str(raw.get("id", "")),
            name=str(raw.get("name", "")),
            mime_type=str(raw.get("mime_type", "")),
            path=str(raw.get("path", "")),
            metadata=dict(raw),
        ))
    return result
