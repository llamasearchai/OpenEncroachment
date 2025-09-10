from __future__ import annotations

import csv
import pathlib
from typing import Any

from open_encroachment.utils.io import gen_id, now_iso


def ingest(
    config: dict[str, Any],
    path: str = "data/social/sample_social.csv",
) -> list[dict[str, Any]]:
    """Ingest social posts; optional columns: text, lat, lon, timestamp, source.
    Falls back to None for lat/lon if missing.
    """
    events: list[dict[str, Any]] = []
    p = pathlib.Path(path)
    if not p.exists():
        return events
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            text = (r.get("text") or "").strip()
            lat: float | None = None
            lon: float | None = None
            try:
                if r.get("lat") not in (None, ""):
                    lat = float(r["lat"])  # may raise
                if r.get("lon") not in (None, ""):
                    lon = float(r["lon"])  # may raise
            except Exception:
                lat, lon = None, None
            evt = {
                "id": gen_id("soc"),
                "source": r.get("source") or "social",
                "timestamp": r.get("timestamp") or now_iso(),
                "lat": lat,
                "lon": lon,
                "features": {"text": text},
                "artifacts": {"raw": r},
            }
            events.append(evt)
    return events
