from __future__ import annotations

from typing import Any

import joblib
import numpy as np

from ..nlp.nlp_engine import SocialNLP


class ThreatClassifier:
    def __init__(self, model_dir: str = "artifacts/models") -> None:
        self.model_dir = model_dir
        self.model_path = f"{model_dir}/fused_clf.joblib"
        self.nlp = SocialNLP(model_dir=model_dir)
        self.model = self._load_model()

    def _load_model(self):
        try:
            return joblib.load(self.model_path)
        except Exception:
            return None

    def _baseline_probability(self, features: dict[str, float], text_score: float, in_geofence: bool) -> float:
        # Simple heuristic combining available signals into [0,1]
        score = 0.0
        weights = {
            "img_edge_strength": 0.15,
            "img_texture": 0.1,
            "aerial_edge_strength": 0.15,
            "aerial_texture": 0.1,
            "ground_sensor_pm25_z": 0.1,
            "ground_sensor_noise_db_z": 0.1,
            "ground_sensor_vibration_z": 0.1,
            "ground_sensor_temp_c_z": 0.05,
        }
        # Accumulate weighted normalized values
        for k, w in weights.items():
            if k in features:
                val = float(features[k])
                score += w * float(1.0 / (1.0 + np.exp(-val)))
        # Include NLP text score
        score += 0.25 * float(text_score)
        # Geofence bonus
        if in_geofence:
            score = min(1.0, score + 0.1)
        return float(np.clip(score, 0.0, 1.0))

    def classify(self, fused_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for e in fused_events:
            text_score = self.nlp.threat_score(e.get("texts", []))
            f = e.get("features", {})
            # Normalize ground sensor feature names (from ingestion)
            norm = {}
            for k, v in f.items():
                if k.startswith("ground_sensor_"):
                    norm[f"ground_sensor_{k.split('ground_sensor_')[1]}"] = v
                else:
                    norm[k] = v
            prob = self._baseline_probability(norm, text_score, bool(e.get("in_geofence")))
            results.append({
                "id": e["id"],
                "timestamp": e["timestamp"],
                "lat": e.get("lat"),
                "lon": e.get("lon"),
                "geofence_id": e.get("geofence_id"),
                "in_geofence": e.get("in_geofence", False),
                "threat_probability": prob,
                "text_threat": text_score,
                "features": norm,
                "sources": e.get("sources", []),
                "raw_event_ids": e.get("raw_event_ids", []),
            })
        return results

