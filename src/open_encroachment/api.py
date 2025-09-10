"""
OpenEncroachment FastAPI Application

Provides REST API endpoints for the OpenEncroachment threat detection system.
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agents.agent import run_agent
from .case_management.case_manager import CaseManager
from .comms.dispatcher import Dispatcher
from .config import load_config
from .evidence.chain_of_custody import verify_ledger
from .pipeline import run_pipeline


class AgentRequest(BaseModel):
    """Request model for agent interactions."""

    prompt: str
    model: str = "gpt-4o-mini"


class PipelineRequest(BaseModel):
    """Request model for pipeline execution."""

    config_path: str | None = None
    use_sample_data: bool = False


class NotificationRequest(BaseModel):
    """Request model for notifications."""

    incident_id: str
    config_path: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    yield
    # Shutdown


app = FastAPI(
    title="OpenEncroachment API",
    description="REST API for the OpenEncroachment threat detection system",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "OpenEncroachment API", "version": "1.0.0"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/v1/agent/run")
async def agent_run(request: AgentRequest) -> dict[str, Any]:
    """Run the OpenEncroachment agent with a prompt."""
    try:
        result = run_agent(
            prompt=request.prompt,
            model=request.model,
        )
        if not result.get("ok"):
            raise HTTPException(
                status_code=500, detail=result.get("error", "Agent execution failed")
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/pipeline/run")
async def pipeline_run(request: PipelineRequest) -> dict[str, Any]:
    """Execute the complete pipeline."""
    try:
        result = run_pipeline(
            config_path=request.config_path,
            use_sample_data=request.use_sample_data,
        )
        return {"ok": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/cases")
async def get_cases(config_path: str | None = None, limit: int = 20) -> dict[str, Any]:
    """Get case/incident data."""
    try:
        cfg = load_config(config_path)
        cm = CaseManager(
            db_path=cfg.get("artifacts", {}).get("db_path", "artifacts/case_manager.db")
        )
        cases = cm.list_cases(limit=limit)
        return {"ok": True, "cases": cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/incidents")
async def get_incidents(config_path: str | None = None, limit: int = 20) -> dict[str, Any]:
    """Get incident data."""
    try:
        cfg = load_config(config_path)
        cm = CaseManager(
            db_path=cfg.get("artifacts", {}).get("db_path", "artifacts/case_manager.db")
        )
        incidents = cm.list_incidents(limit=limit)
        return {"ok": True, "incidents": incidents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/notifications")
async def create_notification(request: NotificationRequest) -> dict[str, Any]:
    """Create and send a notification for an incident."""
    try:
        cfg = load_config(request.config_path)
        cm = CaseManager(
            db_path=cfg.get("artifacts", {}).get("db_path", "artifacts/case_manager.db")
        )

        # Find the incident
        incidents = cm.list_incidents(limit=1000)
        incident = next((inc for inc in incidents if inc["id"] == request.incident_id), None)

        if not incident:
            raise HTTPException(status_code=404, detail=f"Incident {request.incident_id} not found")

        # Send notification
        dispatcher = Dispatcher(cfg)
        dispatcher.notify(
            {
                "id": incident["id"],
                "timestamp": incident["timestamp"],
                "location": {
                    "lat": incident.get("lat"),
                    "lon": incident.get("lon"),
                    "geofence_id": incident.get("geofence_id"),
                },
                "threat_probability": incident.get("threat_probability", 0.0),
                "severity": incident.get("severity", {}),
                "sources": incident.get("sources", []),
            }
        )

        return {"ok": True, "message": f"Notification sent for incident {request.incident_id}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/evidence/verify")
async def verify_evidence(config_path: str | None = None) -> dict[str, Any]:
    """Verify evidence ledger integrity."""
    try:
        cfg = load_config(config_path)
        ok, count = verify_ledger(cfg)
        return {
            "ok": ok,
            "checked": count,
            "status": "verified" if ok else "integrity_check_failed",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analytics/severity")
async def get_severity_summary(config_path: str | None = None, limit: int = 100) -> dict[str, Any]:
    """Get severity summary for incidents."""
    try:
        cfg = load_config(config_path)
        cm = CaseManager(
            db_path=cfg.get("artifacts", {}).get("db_path", "artifacts/case_manager.db")
        )
        incidents = cm.list_incidents(limit=limit)

        buckets = {"high": 0, "medium": 0, "low": 0}
        details = []

        for inc in incidents:
            sev = float(inc.get("severity_overall", 0.0))
            if sev >= 0.8:
                buckets["high"] += 1
            elif sev >= 0.6:
                buckets["medium"] += 1
            else:
                buckets["low"] += 1

            details.append(
                {
                    "id": inc["id"],
                    "timestamp": inc["timestamp"],
                    "geofence_id": inc.get("geofence_id"),
                    "severity": sev,
                    "threat_probability": float(inc.get("threat_probability", 0.0)),
                }
            )

        return {"ok": True, "buckets": buckets, "count": len(incidents), "details": details[:10]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
