import json
import subprocess


def test_cli_run_pipeline_sample():
    # Run the CLI pipeline with sample data and parse JSON output
    proc = subprocess.run(
        [
            "open-encroachment",
            "--config",
            "config/settings.yaml",
            "run-pipeline",
            "--sample-data",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    # Basic shape checks
    assert "events" in data
    assert "incidents" in data
    assert isinstance(data["events"], int)
    assert isinstance(data["incidents"], int)
