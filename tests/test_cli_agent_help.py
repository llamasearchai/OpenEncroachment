import subprocess


def test_agent_cli_help():
    # Ensure the agent CLI shows help and does not require API key
    proc = subprocess.run(
        [
            "open-encroachment",
            "agent",
            "run",
            "--help",
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    # Basic shape checks
    assert "Usage:" in proc.stdout
    assert "open_encroachment.agents.cli" in proc.stdout
