from open_encroachment.case_management.case_manager import CaseManager


def test_case_manager_create_update(tmp_path):
    db_path = tmp_path / "cm.db"
    cm = CaseManager(db_path=str(db_path))
    # Seed one incident
    inc = {
        "id": "inc_local",
        "timestamp": "2025-01-01T00:00:00+00:00",
        "lat": 1.0,
        "lon": 2.0,
        "geofence_id": "gf1",
        "in_geofence": 1,
        "threat_probability": 0.7,
        "text_threat": 0.5,
        "severity": {
            "overall": 0.75,
            "environmental": 0.6,
            "legal": 0.7,
            "operational": 0.65,
        },
        "sources": ["unit"],
        "features": {},
    }
    cm.record_incidents([inc])
    # Create and update a case
    cid = cm.create_case("inc_local", assigned_to="ops", status="open")
    assert isinstance(cid, int) and cid > 0
    cm.update_case_status(cid, "closed")
    cases = cm.list_cases(limit=5)
    assert any(c["id"] == cid and c["status"] == "closed" for c in cases)
