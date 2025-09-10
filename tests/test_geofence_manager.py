"""
Tests for the GeofenceManager class.
"""

import pytest

from open_encroachment.geofencing.geofence_manager import GeofenceManager


class TestGeofenceManager:
    """Test cases for GeofenceManager."""

    @pytest.fixture
    def sample_geofences(self):
        """Sample geofence data for testing."""
        return [
            {
                "id": "test_area_1",
                "name": "Test Conservation Area 1",
                "polygon": [
                    [37.3317, -122.0301],
                    [37.3317, -122.0000],
                    [37.3510, -122.0000],
                    [37.3510, -122.0301],
                ],
            },
            {
                "id": "test_area_2",
                "name": "Test Conservation Area 2",
                "polygon": [
                    [37.3617, -122.0301],
                    [37.3617, -122.0000],
                    [37.3810, -122.0000],
                    [37.3810, -122.0301],
                ],
            },
        ]

    @pytest.fixture
    def manager(self, sample_geofences):
        """GeofenceManager instance for testing."""
        return GeofenceManager(sample_geofences)

    def test_initialization(self):
        """Test GeofenceManager initialization."""
        manager = GeofenceManager()
        assert manager.geofences == []

        manager_with_data = GeofenceManager([{"id": "test"}])
        assert len(manager_with_data.geofences) == 1

    def test_add_geofence(self, manager):
        """Test adding a geofence."""
        initial_count = len(manager.geofences)
        new_geofence = {
            "id": "new_area",
            "name": "New Test Area",
            "polygon": [[0, 0], [0, 1], [1, 1], [1, 0]],
        }
        manager.add_geofence(new_geofence)
        assert len(manager.geofences) == initial_count + 1
        assert manager.geofences[-1] == new_geofence

    def test_remove_geofence(self, manager):
        """Test removing a geofence."""
        initial_count = len(manager.geofences)
        success = manager.remove_geofence("test_area_1")
        assert success
        assert len(manager.geofences) == initial_count - 1

        # Try to remove non-existent geofence
        success = manager.remove_geofence("non_existent")
        assert not success
        assert len(manager.geofences) == initial_count - 1

    def test_contains_point(self, manager):
        """Test point containment checking."""
        # Point inside first geofence
        inside, geofence_id = manager.contains_point(37.3417, -122.0151)
        assert inside
        assert geofence_id == "test_area_1"

        # Point outside all geofences
        inside, geofence_id = manager.contains_point(37.3000, -122.0500)
        assert not inside
        assert geofence_id is None

    def test_get_geofence(self, manager):
        """Test getting geofence by ID."""
        gf = manager.get_geofence("test_area_1")
        assert gf is not None
        assert gf["id"] == "test_area_1"

        gf = manager.get_geofence("non_existent")
        assert gf is None

    def test_list_geofences(self, manager, sample_geofences):
        """Test listing all geofences."""
        geofences = manager.list_geofences()
        assert len(geofences) == len(sample_geofences)
        assert geofences == sample_geofences

        # Ensure it's a copy, not the original
        geofences[0]["name"] = "Modified"
        assert manager.geofences[0]["name"] != "Modified"

    def test_distance_to_geofence(self, manager):
        """Test distance calculation to geofence."""
        # Point inside geofence should return 0
        distance = manager.distance_to_geofence(37.3417, -122.0151, "test_area_1")
        assert distance == 0.0

        # Point outside geofence
        distance = manager.distance_to_geofence(37.3000, -122.0500, "test_area_1")
        assert distance is not None
        assert distance > 0

        # Non-existent geofence
        distance = manager.distance_to_geofence(37.3417, -122.0151, "non_existent")
        assert distance is None

    def test_get_geofence_stats(self, manager):
        """Test getting geofence statistics."""
        stats = manager.get_geofence_stats()
        assert stats["total_geofences"] == 2
        assert "test_area_1" in stats["geofence_ids"]
        assert "test_area_2" in stats["geofence_ids"]
        assert "Test Conservation Area 1" in stats["geofence_names"]
        assert "Test Conservation Area 2" in stats["geofence_names"]
