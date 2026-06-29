from evolution.learning_engine import LearningService


service = LearningService()

record = service.record_experience(
    source_type="proposal",
    source_id="proposal_smoke_001",
    title="OEP-006.1 Learning Memory Smoke",
    summary="Proposal outcome recorded as learning memory.",
    outcome="success",
    score=0.91,
    lessons=["Governed learning memory can record outcomes without execution."],
    tags=["oep006", "learning", "memory"],
    metadata={"baseline": "v0.6.0-beta"},
)

records = service.list_experiences()
by_source = service.find_by_source("proposal_smoke_001")
summary = service.summarize_learning()

assert record["memory_id"].startswith("lmem_")
assert record["proposal_only"] is True
assert record["write_executed"] is False
assert record["human_approval_required"] is True
assert record["outcome"] == "success"
assert 0.0 <= record["score"] <= 1.0
assert len(records) == 1
assert len(by_source) == 1
assert summary["total"] == 1
assert summary["outcomes"]["success"] == 1

print("OEP006_1_LEARNING_MEMORY_PASS")
