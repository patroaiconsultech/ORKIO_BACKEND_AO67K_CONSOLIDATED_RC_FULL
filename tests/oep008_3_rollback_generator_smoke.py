from evolution.governed_evolution import RollbackGenerator
rollback=RollbackGenerator().generate(["evolution/governed_evolution/rollback.py"])
assert rollback["strategy"]=="restore_previous_version"
assert len(rollback["steps"])>=3
assert rollback["proposal_only"] is True
assert rollback["write_executed"] is False
assert rollback["human_approval_required"] is True
print("OEP008_3_ROLLBACK_GENERATOR_PASS")
