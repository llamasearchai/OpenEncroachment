import json
import subprocess


def test_ledger_verify_cli():
    # Run the CLI evidence verification; it will succeed even if the ledger file is absent
    proc = subprocess.run(
        ["open-encroachment", "--config", "config/settings.yaml", "evidence"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert "ok" in data
