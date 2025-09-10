# OpenEncroachment API Documentation

This document provides detailed information about the OpenEncroachment REST API endpoints.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API does not require authentication. In production deployments, consider adding API key authentication.

## Endpoints

### System Information

#### GET /
Returns basic system information.

**Response:**
```json
{
  "message": "OpenEncroachment API",
  "version": "1.0.0"
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### Pipeline Operations

#### POST /api/v1/pipeline/run
Executes the complete threat detection pipeline.

**Request Body:**
```json
{
  "config_path": "config/settings.yaml",
  "use_sample_data": true
}
```

**Parameters:**
- `config_path` (optional): Path to configuration file
- `use_sample_data` (optional): Generate and use sample data

**Response:**
```json
{
  "ok": true,
  "result": {
    "events": 45,
    "fused": 23,
    "incidents": 12,
    "notified": ["incident-123", "incident-456"],
    "risk_geofences": [...],
    "geofence_breaches": {
      "conservation_area": 5,
      "protected_zone": 2
    }
  }
}
```

### AI Agent

#### POST /api/v1/agent/run
Interacts with the OpenAI Agents SDK powered assistant.

**Request Body:**
```json
{
  "prompt": "Analyze current threat levels",
  "model": "gpt-4o-mini"
}
```

**Parameters:**
- `prompt` (required): User prompt for the agent
- `model` (optional): OpenAI model to use (default: gpt-4o-mini)

**Response:**
```json
{
  "ok": true,
  "output": "Based on the current data, there are 3 high-severity incidents...",
  "model": "gpt-4o-mini",
  "agent_name": "OpenEncroachment Assistant"
}
```

### Case Management

#### GET /api/v1/cases
Retrieves incident cases.

**Query Parameters:**
- `config_path`: Path to configuration file
- `limit`: Maximum number of cases to return (default: 20)

**Response:**
```json
{
  "ok": true,
  "cases": [
    {
      "id": "case-001",
      "title": "Illegal dumping incident",
      "status": "active",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

#### GET /api/v1/incidents
Retrieves individual incidents.

**Query Parameters:**
- `config_path`: Path to configuration file
- `limit`: Maximum number of incidents to return (default: 20)

**Response:**
```json
{
  "ok": true,
  "incidents": [
    {
      "id": "incident-123",
      "timestamp": "2025-01-01T12:00:00Z",
      "lat": 37.3417,
      "lon": -122.0151,
      "threat_probability": 0.85,
      "severity_overall": 0.72,
      "geofence_id": "conservation_area",
      "in_geofence": true
    }
  ]
}
```

### Notifications

#### POST /api/v1/notifications
Creates and sends a notification for a specific incident.

**Request Body:**
```json
{
  "incident_id": "incident-123",
  "config_path": "config/settings.yaml"
}
```

**Response:**
```json
{
  "ok": true,
  "message": "Notification sent for incident incident-123"
}
```

### Evidence Management

#### GET /api/v1/evidence/verify
Verifies the integrity of the evidence ledger.

**Query Parameters:**
- `config_path`: Path to configuration file

**Response:**
```json
{
  "ok": true,
  "checked": 150,
  "status": "verified"
}
```

### Analytics

#### GET /api/v1/analytics/severity
Retrieves severity analytics for incidents.

**Query Parameters:**
- `config_path`: Path to configuration file
- `limit`: Maximum incidents to analyze (default: 100)

**Response:**
```json
{
  "ok": true,
  "buckets": {
    "high": 3,
    "medium": 8,
    "low": 15
  },
  "count": 26,
  "details": [
    {
      "id": "incident-123",
      "timestamp": "2025-01-01T12:00:00Z",
      "geofence_id": "conservation_area",
      "severity": 0.85,
      "threat_probability": 0.72
    }
  ]
}
```

## Error Responses

All endpoints return error responses in the following format:

```json
{
  "ok": false,
  "error": "Description of the error"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

Currently, there are no rate limits implemented. In production, consider adding rate limiting based on your requirements.

## Data Formats

### Timestamps
All timestamps are in ISO 8601 format with timezone information:
```
2025-01-01T12:00:00Z
2025-01-01T12:00:00+00:00
```

### Coordinates
Latitude and longitude are in decimal degrees:
- Latitude: -90 to 90
- Longitude: -180 to 180

### Severity Scores
Severity scores are normalized between 0.0 and 1.0:
- 0.0: No threat
- 1.0: Maximum threat

## WebSocket Support

The API currently does not support WebSockets. For real-time updates, consider implementing Server-Sent Events (SSE) or WebSocket endpoints in future versions.

## Versioning

The API uses URL versioning (`/api/v1/`). Future versions will maintain backward compatibility where possible.
