from evolution.governed_evolution import DiffPreviewGenerator
preview=DiffPreviewGenerator().generate(["evolution/governed_evolution/diff_preview.py"],"Preview only")
assert preview["files_changed"]==["evolution/governed_evolution/diff_preview.py"]
assert preview["diff_generated"] is False
assert preview["proposal_only"] is True
assert preview["write_executed"] is False
assert preview["human_approval_required"] is True
print("OEP008_2_DIFF_PREVIEW_PASS")
