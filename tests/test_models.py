import pytest

from open_encroachment.models.schemas import Event, Incident, Location


def test_event_validation():
    valid = {
        "id": "test_id",
        "source": "test",
        "timestamp": "2025-01-01T12:00:00Z",
        "lat": 37.0,
        "lon": -122.0,
        "features": {"key": "value"},
        "artifacts": {"path": "test.jpg"},
    }
    event = Event(**valid)
    assert event.id == "test_id"
    assert event.source == "test"


def test_event_invalid_timestamp():
    invalid = {"id": "id", "source": "src", "timestamp": "invalid", "features": {}}
    with pytest.raises(ValueError):
        Event(**invalid)


def test_incident_severity():
    inc = {
        "id": "inc_id",
        "timestamp": "2025-01-01T12:00:00Z",
        "in_geofence": False,
        "threat_probability": 0.5,
        "text_threat": 0.3,
        "features": {},
        "sources": [],
        "raw_event_ids": [],
        "severity": {"environmental": 0.4, "legal": 0.6, "operational": 0.5, "overall": 0.5},
    }
    incident = Incident(**inc)
    assert incident.threat_probability == 0.5
    assert incident.severity.overall == 0.5


def test_incident_invalid_severity():
    inc = {
        "id": "inc_id",
        "timestamp": "2025-01-01T12:00:00Z",
        "in_geofence": False,
        "threat_probability": 0.5,
        "text_threat": 0.3,
        "features": {},
        "sources": [],
        "raw_event_ids": [],
        "severity": {
            "environmental": 1.5,
            "legal": 0.0,
            "operational": 0.0,
            "overall": 0.0,
        },  # Invalid >1
    }
    with pytest.raises(ValueError):
        Incident(**inc)


def test_location_bounds():
    loc = Location(lat=90.0, lon=180.0)
    assert loc.lat == 90.0
    assert loc.lon == 180.0
    with pytest.raises(ValueError):
        Location(lat=91.0, lon=181.0)
