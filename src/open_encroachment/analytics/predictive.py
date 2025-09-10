from __future__ import annotations

import csv
import pathlib
from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any


def _parse_ts(s: str) -> datetime:
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def predict_geofence_risk(
    config: dict[str, Any],
    incidents: Iterable[dict[str, Any]],
    horizon_days: int = 30,
    out_csv: str = "artifacts/predictions/risk_map.csv",
) -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=horizon_days)
    scores: dict[str, list[float]] = defaultdict(list)
    for inc in incidents:
        ts = _parse_ts(inc.get("timestamp", ""))
        if ts < cutoff:
            continue
        gf = inc.get("geofence_id") or "unknown"
        sev = float(inc.get("severity", {}).get("overall", 0.0))
        scores[gf].append(sev)
    results: list[dict[str, Any]] = []
    for gf, vals in scores.items():
        if vals:
            risk = sum(vals) / len(vals)
        else:
            risk = 0.0
        results.append({"geofence_id": gf, "risk": round(risk, 4), "count": len(vals)})
    # Write CSV
    p = pathlib.Path(out_csv)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["geofence_id", "risk", "count"])
        w.writeheader()
        for row in results:
            w.writerow(row)
    return results

