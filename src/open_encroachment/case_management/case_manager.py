from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from typing import Any

from open_encroachment.utils.io import ensure_dir


class CaseManager:
    def __init__(self, db_path: str = "artifacts/case_manager.db") -> None:
        self.db_path = db_path
        ensure_dir("artifacts")
        self._init_db()

    def _init_db(self) -> None:
        con = sqlite3.connect(self.db_path)
        try:
            cur = con.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    lat REAL,
                    lon REAL,
                    geofence_id TEXT,
                    in_geofence INTEGER,
                    threat_probability REAL,
                    text_threat REAL,
                    severity_overall REAL,
                    severity_environmental REAL,
                    severity_legal REAL,
                    severity_operational REAL,
                    sources TEXT,
                    features TEXT
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT,
                    status TEXT,
                    assigned_to TEXT,
                    created_at TEXT,
                    updated_at TEXT
                );
                """
            )
            con.commit()
        finally:
            con.close()

    def record_incidents(self, incidents: Iterable[dict[str, Any]]) -> None:
        con = sqlite3.connect(self.db_path)
        try:
            cur = con.cursor()
            for inc in incidents:
                sev = inc.get("severity", {})
                cur.execute(
                    """
                    INSERT OR REPLACE INTO incidents (
                        id, timestamp, lat, lon, geofence_id, in_geofence,
                        threat_probability, text_threat,
                        severity_overall, severity_environmental, severity_legal, severity_operational,
                        sources, features
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        inc.get("id"),
                        inc.get("timestamp"),
                        inc.get("lat"),
                        inc.get("lon"),
                        inc.get("geofence_id"),
                        1 if inc.get("in_geofence") else 0,
                        float(inc.get("threat_probability", 0.0)),
                        float(inc.get("text_threat", 0.0)),
                        float(sev.get("overall", 0.0)),
                        float(sev.get("environmental", 0.0)),
                        float(sev.get("legal", 0.0)),
                        float(sev.get("operational", 0.0)),
                        json.dumps(inc.get("sources", [])),
                        json.dumps(inc.get("features", {})),
                    ),
                )
            con.commit()
        finally:
            con.close()

    def list_incidents(self, limit: int = 50) -> list[dict[str, Any]]:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        try:
            cur = con.cursor()
            cur.execute("SELECT * FROM incidents ORDER BY timestamp DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            con.close()

    def create_case(self, incident_id: str, assigned_to: str = "", status: str = "open") -> int:
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).isoformat()
        con = sqlite3.connect(self.db_path)
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO cases (incident_id, status, assigned_to, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (incident_id, status, assigned_to, ts, ts),
            )
            con.commit()
            return int(cur.lastrowid)
        finally:
            con.close()

    def update_case_status(self, case_id: int, status: str) -> None:
        from datetime import datetime, timezone

        ts = datetime.now(timezone.utc).isoformat()
        con = sqlite3.connect(self.db_path)
        try:
            cur = con.cursor()
            cur.execute("UPDATE cases SET status=?, updated_at=? WHERE id=?", (status, ts, case_id))
            con.commit()
        finally:
            con.close()

    def list_cases(self, limit: int = 50) -> list[dict[str, Any]]:
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        try:
            cur = con.cursor()
            cur.execute("SELECT * FROM cases ORDER BY id DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        finally:
            con.close()
