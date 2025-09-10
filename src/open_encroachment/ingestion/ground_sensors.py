from __future__ import annotations

import csv
import pathlib
from statistics import mean, pstdev
from typing import Any

from ..utils.io import gen_id, now_iso


def ingest(config: dict[str, Any], data_path: str = "data/ground/ground_sensors.csv") -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    p = pathlib.Path(data_path)
    if not p.exists():
        return events
    rows: list[dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                rows.append({
                    "timestamp": r.get("timestamp") or now_iso(),
                    "lat": float(r["lat"]),
                    "lon": float(r["lon"]),
                    "pm25": float(r.get("pm25", 0) or 0),
                    "noise_db": float(r.get("noise_db", 0) or 0),
                    "vibration": float(r.get("vibration", 0) or 0),
                    "temp_c": float(r.get("temp_c", 0) or 0),
                })
            except Exception:
                continue
    if not rows:
        return events
    # Compute simple z-score anomalies per metric
    metrics = ["pm25", "noise_db", "vibration", "temp_c"]
    stats = {}
    for m in metrics:
        vals = [r[m] for r in rows]
        mu = mean(vals)
        sigma = pstdev(vals) or 1.0
        stats[m] = (mu, sigma)
    for r in rows:
        feats = {}
        for m in metrics:
            mu, sigma = stats[m]
            feats[f"{m}_z"] = (r[m] - mu) / sigma
        evt = {
            "id": gen_id("gnd"),
            "source": "ground_sensor",
            "timestamp": r["timestamp"],
            "lat": r["lat"],
            "lon": r["lon"],
            "features": feats,
            "artifacts": {"row": r},
        }
        events.append(evt)
    return events

