from __future__ import annotations

import numpy as np


def severity_score(
    threat_prob: float,
    features: dict[str, float],
    in_geofence: bool,
    geofence_id: str | None,
) -> dict[str, float]:
    """Compute severity sub-scores and overall severity in [0,1].
    - environmental: proxy via sensor anomalies and image/aerial signals
    - legal: boosted if inside geofence and high NLP/specific cues
    - operational: boosted by multi-source corroboration and proximity to assets (if provided)
    """
    # Environmental impact
    env_terms = [
        features.get("ground_sensor_pm25_z", 0.0),
        features.get("ground_sensor_noise_db_z", 0.0),
        features.get("ground_sensor_vibration_z", 0.0),
        features.get("img_edge_strength", 0.0),
        features.get("aerial_edge_strength", 0.0),
    ]
    env = float(1 / (1 + np.exp(-np.mean(env_terms)))) if env_terms else 0.0

    # Legal implications
    legal = float(threat_prob)
    if in_geofence:
        legal = min(1.0, legal + 0.2)

    # Operational risk
    corroboration = 0.0
    # Use presence of multiple modalities as proxy
    if any(k.startswith("img_") for k in features) and any(k.startswith("aerial_") for k in features):
        corroboration += 0.2
    if any(k.startswith("ground_sensor_") for k in features):
        corroboration += 0.2
    operational = min(1.0, 0.5 * threat_prob + corroboration)

    overall = float(np.clip(0.4 * env + 0.3 * legal + 0.3 * operational, 0.0, 1.0))

    return {
        "environmental": float(np.clip(env, 0.0, 1.0)),
        "legal": float(np.clip(legal, 0.0, 1.0)),
        "operational": float(np.clip(operational, 0.0, 1.0)),
        "overall": overall,
    }

