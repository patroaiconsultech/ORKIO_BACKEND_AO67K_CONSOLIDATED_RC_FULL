from services.orion_premium.execution_receipts import (
    build_execution_receipt,
    verify_execution_receipt,
)


def test_success_receipt_contains_hash():
    receipt = build_execution_receipt(
        task_id="t1",
        tool_name="example",
        started_at="2026-07-22T00:00:00+00:00",
        success=True,
        output={"ok": True},
    )
    result = verify_execution_receipt(receipt)
    assert receipt.output_hash
    assert result["verified"] is True


def test_failed_receipt_requires_error_code():
    receipt = build_execution_receipt(
        task_id="t1",
        tool_name="example",
        started_at="2026-07-22T00:00:00+00:00",
        success=False,
    )
    result = verify_execution_receipt(receipt)
    assert "error_code_missing" in result["failures"]
