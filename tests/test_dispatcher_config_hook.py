import json

from open_encroachment.comms.dispatcher import Dispatcher


def test_dispatcher_reads_external_yaml(tmp_path):
    # Create external dispatcher config YAML
    dcfg = {
        "mode": "webhook",
        "webhook": {
            "url": "https://example.org/webhook",
            "timeout": 5.0,
            "headers": {"X-Test": "1"},
        },
    }
    path = tmp_path / "dispatcher.yaml"
    path.write_text(json.dumps(dcfg), encoding="utf-8")

    outbox = tmp_path / "outbox"
    cfg = {
        "dispatch": {"mode": "webhook", "outbox_dir": str(outbox)},
        "dispatch_config_path": str(path),
    }
    disp = Dispatcher(cfg)
    # Should not error even if webhook attempt fails (suppressed)
    inc = {
        "id": "inc_1",
        "timestamp": "2025-01-01T00:00:00+00:00",
        "location": {"lat": 0.0, "lon": 0.0, "geofence_id": "gf"},
        "threat_probability": 0.5,
        "severity": {"overall": 0.6},
        "sources": ["test"],
    }
    disp.notify(inc)
    files = list(outbox.glob("notice_*.json"))
    assert files, "No notice file written"
