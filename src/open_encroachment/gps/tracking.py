from __future__ import annotations

import csv
import pathlib
from typing import Any

from open_encroachment.utils.io import gen_id


def ingest_tracks(path: str = "data/gps/gps_events.csv") -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    p = pathlib.Path(path)
    if not p.exists():
        return events
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                events.append(
                    {
                        "id": gen_id("gps"),
                        "source": "gps",
                        "timestamp": r.get("timestamp"),
                        "lat": float(r.get("lat")),
                        "lon": float(r.get("lon")),
                        "features": {},
                        "artifacts": {"raw": r},
                    }
                )
            except Exception:
                continue
    return events
