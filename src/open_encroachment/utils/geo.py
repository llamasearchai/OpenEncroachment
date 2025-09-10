from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Any

# Earth radius in meters
EARTH_R = 6371000.0


def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two lat/lon points in meters."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_R * c


def point_in_polygon(lat: float, lon: float, polygon: Iterable[tuple[float, float]]) -> bool:
    """Ray-casting algorithm to determine if a point is inside a polygon.
    polygon: iterable of (lat, lon) vertices.
    """
    x = lon
    y = lat
    inside = False
    points: list[tuple[float, float]] = list(polygon)
    n = len(points)
    if n < 3:
        return False
    for i in range(n):
        y1, x1 = points[i]
        y2, x2 = points[(i + 1) % n]
        # Check if point is between y1 and y2
        if (y1 > y) != (y2 > y):
            # Compute intersection of polygon edge with horizontal ray from point
            xinters = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1
            if x < xinters:
                inside = not inside
    return inside


def any_geofence_contains(
    lat: float, lon: float, geofences: list[dict[str, Any]]
) -> tuple[bool, str | None]:
    """Return (inside, geofence_id) for first geofence that contains point."""
    for gf in geofences:
        polygon = gf.get("polygon", [])
        if not polygon:
            continue
        if point_in_polygon(lat, lon, polygon):
            return True, gf.get("id") or gf.get("name")
    return False, None
