def test_knowledge_fabric_imports():
    from knowledge_fabric.google_drive.policy import DEFAULT_POLICY, enforce_policy
    from knowledge_fabric.google_drive.models import DriveInventoryItem
    from knowledge_fabric.google_drive.classifier import classify_drive_item

    assert DEFAULT_POLICY["mode"] == "inventory_only"
    assert DEFAULT_POLICY["runtime_use_allowed"] is False

    item = DriveInventoryItem(
        drive_file_id="test",
        name="Master Plan ORKIO.docx",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    result = classify_drive_item(item)
    assert result.runtime_use_allowed is False
    assert result.requires_human_approval is True

    try:
        enforce_policy("direct_runtime_rag")
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe mode was not blocked")
