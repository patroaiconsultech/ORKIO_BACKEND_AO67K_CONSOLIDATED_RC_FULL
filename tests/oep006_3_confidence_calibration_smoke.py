from evolution.learning_engine import ConfidenceCalibrator

calibrator = ConfidenceCalibrator()
result = calibrator.calibrate(
    base_confidence=0.70,
    outcomes=[
        {"score": 0.90},
        {"score": 0.80},
    ],
)

assert result["sample_size"] == 2
assert result["outcome_mean"] == 0.85
assert 0.70 < result["calibrated_confidence"] <= 1.0
assert result["proposal_only"] is True
assert result["write_executed"] is False
assert result["human_approval_required"] is True

print("OEP006_3_CONFIDENCE_CALIBRATION_PASS")
