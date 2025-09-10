from open_encroachment.pipeline import run_pipeline


def test_pipeline_smoke(tmp_path, monkeypatch):
    # Use a temporary config path; pipeline will fall back to defaults and generate sample data
    result = run_pipeline(config_path=None, use_sample_data=True)
    assert "events" in result
    assert "incidents" in result

