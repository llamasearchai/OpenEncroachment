from __future__ import annotations

import os
import pathlib
from typing import Any

import yaml

DEFAULT_CONFIG = {
    "geofences": [
        {
            "id": "sample_conservation_area",
            "name": "Sample Conservation Area",
            "polygon": [
                [37.3317, -122.0301],
                [37.3317, -122.0000],
                [37.3510, -122.0000],
                [37.3510, -122.0301],
            ],
        }
    ],
    "dispatch": {
        "mode": "local",  # local|webhook
        "outbox_dir": "outbox",
        "webhook_url": None,
        "headers": {},
    },
    "thresholds": {
        "severity_notify_min": 0.6,
        "severity_escalate_min": 0.8
    },
    "artifacts": {
        "models_dir": "artifacts/models",
        "predictions_dir": "artifacts/predictions",
        "db_path": "artifacts/case_manager.db",
        "evidence_ledger": "artifacts/evidence_ledger.jsonl"
    }
}


def load_config(path: str | os.PathLike | None) -> dict[str, Any]:
    """Load YAML config; fall back to DEFAULT_CONFIG if missing."""
    if path is None:
        return DEFAULT_CONFIG
    p = pathlib.Path(path)
    if not p.exists():
        return DEFAULT_CONFIG
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    # Merge shallowly with defaults
    cfg = DEFAULT_CONFIG.copy()
    for k, v in data.items():
        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
            merged = cfg[k].copy()
            merged.update(v)
            cfg[k] = merged
        else:
            cfg[k] = v
    return cfg

