import json

from open_encroachment.comms.dispatcher import Dispatcher


def test_dispatcher_envelope_matches_schema(tmp_path):
    cfg = {"dispatch": {"mode": "local", "outbox_dir": str(tmp_path)}}
    disp = Dispatcher(cfg)
    incident = {
        "id": "inc_test",
        "timestamp": "2025-01-01T12:00:00+00:00",
        "location": {"lat": 1.0, "lon": 2.0, "geofence_id": "gf1"},
        "threat_probability": 0.7,
        "severity": {"overall": 0.8},
        "sources": ["test"],
    }
    disp.notify(incident)
    out = next(tmp_path.glob("notice_*.json"))
    data = json.loads(out.read_text(encoding="utf-8"))
    # Shape checks (schema-like without external dependency)
    assert data["id"] == "inc_test"
    assert data["type"] == "incident.notice"
    assert data["destination"] == "gf1"
    assert "signature" in data and isinstance(data["signature"], str)
    assert set(data.keys()) == {"id", "timestamp", "type", "destination", "payload", "signature"}
    assert set(data["payload"].keys()) >= {"severity", "threat_probability", "location", "sources"}
