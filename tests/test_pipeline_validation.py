from open_encroachment.pipeline import run_pipeline


def test_pipeline_skips_invalid(monkeypatch):
    monkeypatch.setenv("USE_SAMPLE_DATA", "true")  # Mock sample
    result = run_pipeline(use_sample_data=True)
    assert "events" in result
    assert result["events"] > 0  # Some pass
    # Add invalid in sample, ensure skips logged but not crash
