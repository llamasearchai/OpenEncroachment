from typing import Any

from open_encroachment.case_management.case_manager import CaseManager
from open_encroachment.comms.dispatcher import Dispatcher
from open_encroachment.config import load_config
from open_encroachment.pipeline import run_pipeline as _run_pipeline


def run_pipeline(config: str | None = None, sample_data: bool = False) -> dict[str, Any]:
    result = _run_pipeline(config_path=config, use_sample_data=sample_data)
    return {"ok": True, "result": result}


def severity_summary(config: str | None = None, limit: int = 100) -> dict[str, Any]:
    cfg = load_config(config)
    cm = CaseManager(db_path=cfg.get("artifacts", {}).get("db_path", "artifacts/case_manager.db"))
    incs = cm.list_incidents(limit=limit)
    buckets = {"high": 0, "medium": 0, "low": 0}
    details: list[dict[str, Any]] = []
    for inc in incs:
        sev = float(inc.get("severity_overall") or 0.0)
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
                "threat_probability": float(inc.get("threat_probability") or 0.0),
            }
        )
    return {"ok": True, "buckets": buckets, "count": len(incs), "details": details[:10]}


def package_notification(incident_id: str, config: str | None = None) -> dict[str, Any]:
    cfg = load_config(config)
    cm = CaseManager(db_path=cfg.get("artifacts", {}).get("db_path", "artifacts/case_manager.db"))
    incs = cm.list_incidents(limit=1000)
    inc_map = {i["id"]: i for i in incs}
    if incident_id not in inc_map:
        return {"ok": False, "error": f"incident {incident_id} not found"}
    inc = inc_map[incident_id]
    disp = Dispatcher(cfg)
    envelope = {
        "id": inc["id"],
        "timestamp": inc["timestamp"],
        "type": "incident.notice",
        "destination": inc.get("geofence_id") or "unknown",
        "payload": {
            "severity": float(inc.get("severity_overall") or 0.0),
            "threat_probability": float(inc.get("threat_probability") or 0.0),
            "location": {
                "lat": inc.get("lat"),
                "lon": inc.get("lon"),
                "geofence_id": inc.get("geofence_id"),
            },
        },
    }
    # Reuse Dispatcher to sign and write
    disp.notify(
        {
            "id": envelope["id"],
            "timestamp": envelope["timestamp"],
            "location": envelope["payload"]["location"],
            "threat_probability": envelope["payload"]["threat_probability"],
            "severity": {"overall": envelope["payload"]["severity"]},
            "sources": [],
        }
    )
    return {"ok": True, "notice_id": incident_id}


# Tools are now defined as function decorators in agent.py
# This module provides the core tool implementations
