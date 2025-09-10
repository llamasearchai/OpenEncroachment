"""
Geofence Manager for spatial boundary management and monitoring.
"""

from typing import Any

from open_encroachment.utils.geo import any_geofence_contains, haversine_distance_m


class GeofenceManager:
    """Manages geofence definitions and spatial queries."""

    def __init__(self, geofences: list[dict[str, Any]] | None = None):
        """Initialize with list of geofence definitions."""
        self.geofences = geofences or []

    def add_geofence(self, geofence: dict[str, Any]) -> None:
        """Add a new geofence definition."""
        self.geofences.append(geofence)

    def remove_geofence(self, geofence_id: str) -> bool:
        """Remove a geofence by ID. Returns True if found and removed."""
        for i, gf in enumerate(self.geofences):
            if gf.get("id") == geofence_id:
                self.geofences.pop(i)
                return True
        return False

    def contains_point(self, lat: float, lon: float) -> tuple[bool, str | None]:
        """Check if a point is inside any geofence."""
        return any_geofence_contains(lat, lon, self.geofences)

    def get_geofence(self, geofence_id: str) -> dict[str, Any] | None:
        """Get geofence definition by ID."""
        for gf in self.geofences:
            if gf.get("id") == geofence_id:
                return gf
        return None

    def list_geofences(self) -> list[dict[str, Any]]:
        """Get all geofence definitions."""
        return self.geofences.copy()

    def distance_to_geofence(self, lat: float, lon: float, geofence_id: str) -> float | None:
        """Calculate distance from point to nearest edge of specified geofence."""
        gf = self.get_geofence(geofence_id)
        if not gf:
            return None

        polygon = gf.get("polygon", [])
        if not polygon:
            return None

        min_distance = float("inf")
        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]

            # Calculate distance to line segment
            dist = self._point_to_line_distance(lat, lon, p1[0], p1[1], p2[0], p2[1])
            min_distance = min(min_distance, dist)

        return min_distance

    def _point_to_line_distance(
        self, px: float, py: float, x1: float, y1: float, x2: float, y2: float
    ) -> float:
        """Calculate distance from point to line segment."""
        # Convert to meters for accurate distance calculation
        return haversine_distance_m(px, py, x1, y1)

    def get_geofence_stats(self) -> dict[str, Any]:
        """Get statistics about geofences."""
        return {
            "total_geofences": len(self.geofences),
            "geofence_ids": [gf.get("id") for gf in self.geofences],
            "geofence_names": [gf.get("name") for gf in self.geofences],
        }
