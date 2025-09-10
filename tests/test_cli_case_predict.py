import json
import subprocess


def _run_pipeline():
    return subprocess.run(
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


def test_cli_case_incidents_and_list():
    _run_pipeline()  # ensure DB
    proc = subprocess.run(
        [
            "open-encroachment",
            "--config",
            "config/settings.yaml",
            "case",
            "incidents",
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert isinstance(data, list)

    proc2 = subprocess.run(
        [
            "open-encroachment",
            "--config",
            "config/settings.yaml",
            "case",
            "list",
            "--limit",
            "5",
        ],
        capture_output=True,
        text=True,
    )
    assert proc2.returncode == 0, proc2.stderr
    data2 = json.loads(proc2.stdout)
    assert isinstance(data2, list)


def test_cli_predict_risk():
    _run_pipeline()  # ensure incidents exist
    proc = subprocess.run(
        [
            "open-encroachment",
            "--config",
            "config/settings.yaml",
            "predict",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert isinstance(data, list)
    if data:
        assert set(data[0].keys()) >= {"geofence_id", "risk", "count"}
