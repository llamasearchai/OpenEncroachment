from __future__ import annotations

from typing import Any

from .analytics.predictive import predict_geofence_risk
from .case_management.case_manager import CaseManager
from .comms.dispatcher import Dispatcher
from .config import load_config
from .evidence.chain_of_custody import append_records
from .fusion.fusion_engine import fuse_events
from .gps.tracking import ingest_tracks
from .ingestion import aerial, ground_sensors, satellite, social_media
from .models.schemas import Event, FusedEvent, Incident
from .models.severity import severity_score
from .models.threat_classifier import ThreatClassifier
from .utils.io import ensure_dir


def run_pipeline(config_path: str | None = None, use_sample_data: bool = False) -> dict[str, Any]:
    cfg = load_config(config_path)

    # Ensure artifact directories exist
    ensure_dir(cfg.get("artifacts", {}).get("models_dir", "artifacts/models"))
    ensure_dir(cfg.get("artifacts", {}).get("predictions_dir", "artifacts/predictions"))
    ensure_dir(cfg.get("dispatch", {}).get("outbox_dir", "outbox"))

    if use_sample_data:
        _ensure_sample_data()

    raw_events: list[dict[str, Any]] = []
    raw_events += satellite.ingest(cfg)
    raw_events += aerial.ingest(cfg)
    raw_events += ground_sensors.ingest(cfg)
    raw_events += social_media.ingest(cfg)
    raw_events += ingest_tracks()

    events: list[Event] = []
    for raw in raw_events:
        try:
            events.append(Event(**raw))
        except ValueError as err:
            print(f"Skipping invalid event: {err}")
            continue

    # Pass Pydantic Event objects directly; fuser will extract dicts as needed
    raw_fused = fuse_events(events, cfg)
    fused: list[FusedEvent] = []
    for raw in raw_fused:
        try:
            fused.append(FusedEvent(**raw))
        except ValueError as err:
            print(f"Skipping invalid fused event: {err}")
            continue

    clf = ThreatClassifier(model_dir=cfg.get("artifacts", {}).get("models_dir", "artifacts/models"))
    # Classifier expects plain dicts
    raw_classified = clf.classify([fe.model_dump() for fe in fused])

    # Compute severity and persist incidents
    incidents: list[Incident] = []
    for raw_inc in raw_classified:
        severity = severity_score(
            raw_inc.get("threat_probability", 0.0),
            raw_inc.get("features", {}),
            raw_inc.get("in_geofence", False),
            raw_inc.get("geofence_id"),
        )
        raw_inc["severity"] = severity
        try:
            incidents.append(Incident(**raw_inc))
        except ValueError as err:
            print(f"Skipping invalid incident: {err}")
            continue

    cm = CaseManager(db_path=cfg.get("artifacts", {}).get("db_path", "artifacts/case_manager.db"))
    cm.record_incidents([inc.model_dump() for inc in incidents])  # Pass dicts to legacy method

    # Notify
    dispatcher = Dispatcher(cfg)
    th_notify = float(cfg.get("thresholds", {}).get("severity_notify_min", 0.6))
    notified: list[str] = []
    for inc in incidents:
        if inc.severity.overall >= th_notify:
            dispatcher.notify(
                {
                    "id": inc.id,
                    "timestamp": inc.timestamp,
                    "location": {
                        "lat": inc.lat,
                        "lon": inc.lon,
                        "geofence_id": inc.geofence_id,
                    },
                    "threat_probability": inc.threat_probability,
                    "severity": inc.severity.model_dump(),
                    "sources": inc.sources,
                }
            )
            notified.append(inc.id)

    # Evidence chain: add image artifacts if any
    evidence_files: list[str] = []
    for e in events:
        art = e.artifacts
        if "image_path" in art:
            evidence_files.append(art["image_path"])
    if evidence_files:
        for inc in incidents:
            append_records(cfg, inc.model_dump(), evidence_files)
            break

    # Predictive risk map
    risk = predict_geofence_risk(cfg, [inc.model_dump() for inc in incidents])

    # Geofence breach summary
    breach_counts: dict[str, int] = {}
    for inc in incidents:
        if inc.in_geofence:
            key = inc.geofence_id or "unknown"
            breach_counts[key] = breach_counts.get(key, 0) + 1

    return {
        "events": len(events),
        "fused": len(fused),
        "incidents": len(incidents),
        "notified": notified,
        "risk_geofences": risk,
        "geofence_breaches": breach_counts,
    }


def _ensure_sample_data() -> None:
    import csv
    import pathlib

    from PIL import Image

    # Social sample
    social_csv = pathlib.Path("data/social/sample_social.csv")
    social_csv.parent.mkdir(parents=True, exist_ok=True)
    if not social_csv.exists():
        with social_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["timestamp", "source", "text", "lat", "lon"])
            w.writeheader()
            w.writerow(
                {
                    "timestamp": "2025-01-01T12:00:00+00:00",
                    "source": "twitter",
                    "text": "Illegal dumping spotted near river",
                    "lat": 37.34,
                    "lon": -122.015,
                }
            )
            w.writerow(
                {
                    "timestamp": "2025-01-01T12:05:00+00:00",
                    "source": "news",
                    "text": "Construction noise reported downtown",
                    "lat": 37.345,
                    "lon": -122.01,
                }
            )
            w.writerow(
                {
                    "timestamp": "2025-01-01T13:00:00+00:00",
                    "source": "twitter",
                    "text": "Great weather for a hike today",
                    "lat": "",
                    "lon": "",
                }
            )

    # Ground sensors sample
    ground_dir = pathlib.Path("data/ground")
    ground_dir.mkdir(parents=True, exist_ok=True)
    ground_csv = ground_dir / "ground_sensors.csv"
    if not ground_csv.exists():
        with ground_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(
                f, fieldnames=["timestamp", "lat", "lon", "pm25", "noise_db", "vibration", "temp_c"]
            )
            w.writeheader()
            base = [
                ("2025-01-01T11:58:00+00:00", 37.341, -122.017, 12, 45, 0.2, 22),
                ("2025-01-01T12:02:00+00:00", 37.342, -122.016, 55, 78, 0.8, 23),
                ("2025-01-01T12:07:00+00:00", 37.344, -122.014, 30, 60, 0.5, 22.5),
            ]
            for row in base:
                w.writerow(
                    {
                        "timestamp": row[0],
                        "lat": row[1],
                        "lon": row[2],
                        "pm25": row[3],
                        "noise_db": row[4],
                        "vibration": row[5],
                        "temp_c": row[6],
                    }
                )

    # Aerial/Satellite sample images (simple generated squares)
    for sub in ("aerial", "satellite"):
        img_dir = pathlib.Path(f"data/{sub}")
        img_dir.mkdir(parents=True, exist_ok=True)
        img1 = img_dir / "sample1.png"
        if not img1.exists():
            img = Image.new("RGB", (64, 64), color=(200, 200, 200))
            for i in range(64):
                for j in range(64):
                    if 20 < i < 44 and 20 < j < 44:
                        img.putpixel((i, j), (90, 90, 90))
            img.save(img1)

    # GPS sample
    gps_dir = pathlib.Path("data/gps")
    gps_dir.mkdir(parents=True, exist_ok=True)
    gps_csv = gps_dir / "gps_events.csv"
    if not gps_csv.exists():
        with gps_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["timestamp", "lat", "lon"])
            w.writeheader()
            w.writerow({"timestamp": "2025-01-01T12:03:00+00:00", "lat": 37.3425, "lon": -122.0155})
            w.writerow({"timestamp": "2025-01-01T12:06:00+00:00", "lat": 37.3460, "lon": -122.0120})
