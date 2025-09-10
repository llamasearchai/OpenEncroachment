from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..utils.geo import any_geofence_contains, haversine_distance_m
from ..utils.io import gen_id


def _parse_ts(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def fuse_events(
    events: list[dict[str, Any]],
    config: dict[str, Any],
    max_distance_m: float = 500.0,
    max_time_delta_s: int = 600,
) -> list[dict[str, Any]]:
    """Fuse events based on spatio-temporal proximity and enrich with geofence membership."""
    # Separate locatable and non-locatable
    loc: list[tuple[int, dict[str, Any]]] = []
    nloc: list[tuple[int, dict[str, Any]]] = []
    for i, e in enumerate(events):
        if e.get("lat") is not None and e.get("lon") is not None:
            loc.append((i, e))
        else:
            nloc.append((i, e))

    # Sort locatable by time
    loc.sort(key=lambda t: _parse_ts(t[1].get("timestamp", "")))

    clusters: list[list[dict[str, Any]]] = []
    for _, e in loc:
        placed = False
        et = _parse_ts(e.get("timestamp", ""))
        for cl in clusters:
            # Compare with cluster centroid (time/space)
            # Compute centroid lat/lon and median time
            cl_lats = [x["lat"] for x in cl if x.get("lat") is not None]
            cl_lons = [x["lon"] for x in cl if x.get("lon") is not None]
            if not cl_lats or not cl_lons:
                continue
            cl_lat = sum(cl_lats) / len(cl_lats)
            cl_lon = sum(cl_lons) / len(cl_lons)
            d = haversine_distance_m(e["lat"], e["lon"], cl_lat, cl_lon)
            times = sorted(_parse_ts(x.get("timestamp", "")) for x in cl)
            dt = abs((et - times[len(times)//2]).total_seconds())
            if d <= max_distance_m and dt <= max_time_delta_s:
                cl.append(e)
                placed = True
                break
        if not placed:
            clusters.append([e])

    # Attach non-locatable to nearest cluster by time (if close)
    for _, e in nloc:
        et = _parse_ts(e.get("timestamp", ""))
        best_idx: int | None = None
        best_dt = float("inf")
        for i, cl in enumerate(clusters):
            times = sorted(_parse_ts(x.get("timestamp", "")) for x in cl)
            dt = abs((et - times[len(times)//2]).total_seconds())
            if dt < best_dt:
                best_dt = dt
                best_idx = i
        if best_idx is not None and best_dt <= max_time_delta_s:
            clusters[best_idx].append(e)
        else:
            clusters.append([e])

    # Build fused events
    fused: list[dict[str, Any]] = []
    geofences = config.get("geofences", [])
    for cl in clusters:
        # Aggregate features by source, compute centroid lat/lon whenever possible
        lats = [x["lat"] for x in cl if x.get("lat") is not None]
        lons = [x["lon"] for x in cl if x.get("lon") is not None]
        lat = sum(lats) / len(lats) if lats else None
        lon = sum(lons) / len(lons) if lons else None
        feats: dict[str, Any] = {}
        texts: list[str] = []
        for e in cl:
            for k, v in e.get("features", {}).items():
                if k == "text" and isinstance(v, str):
                    texts.append(v)
                else:
                    # Simple namespacing by source
                    feats[f"{e['source']}_{k}"] = v
        inside, gf_id = (False, None)
        if lat is not None and lon is not None:
            inside, gf_id = any_geofence_contains(lat, lon, geofences)
        fused.append({
            "id": gen_id("fused"),
            "timestamp": sorted(_parse_ts(x.get("timestamp", "")) for x in cl)[0].isoformat(),
            "lat": lat,
            "lon": lon,
            "in_geofence": inside,
            "geofence_id": gf_id,
            "features": feats,
            "texts": texts,
            "sources": [e["source"] for e in cl],
            "raw_event_ids": [e["id"] for e in cl],
        })
    return fused

