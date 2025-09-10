from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class Severity(BaseModel):
    environmental: float = Field(..., ge=0.0, le=1.0)
    legal: float = Field(..., ge=0.0, le=1.0)
    operational: float = Field(..., ge=0.0, le=1.0)
    overall: float = Field(..., ge=0.0, le=1.0)


class Event(BaseModel):
    id: str
    source: str
    timestamp: str  # ISO
    lat: float | None = None
    lon: float | None = None
    features: dict[str, Any]
    artifacts: dict[str, Any]

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError as e:
            raise ValueError("Timestamp must be ISO 8601") from e


class FusedEvent(BaseModel):
    id: str
    timestamp: str
    lat: float | None = None
    lon: float | None = None
    in_geofence: bool
    geofence_id: str | None = None
    features: dict[str, Any]
    texts: list[str]
    sources: list[str]
    raw_event_ids: list[str]

    @model_validator(mode="before")
    @classmethod
    def validate_location(cls, values: Any) -> Any:
        if isinstance(values, dict):
            lat = values.get("lat")
            lon = values.get("lon")
            if lat is not None and (lat < -90 or lat > 90):
                raise ValueError("Latitude out of bounds")
            if lon is not None and (lon < -180 or lon > 180):
                raise ValueError("Longitude out of bounds")
        return values


class Incident(BaseModel):
    id: str
    timestamp: str
    lat: float | None = None
    lon: float | None = None
    geofence_id: str | None = None
    in_geofence: bool
    threat_probability: float = Field(..., ge=0.0, le=1.0)
    text_threat: float = Field(..., ge=0.0, le=1.0)
    features: dict[str, Any]
    sources: list[str]
    raw_event_ids: list[str]
    severity: Severity
