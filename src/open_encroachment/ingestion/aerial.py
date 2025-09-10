from __future__ import annotations

import itertools
import pathlib
from typing import Any

import numpy as np
from PIL import Image, ImageFilter

from ..utils.io import gen_id, now_iso


def _image_features(img: Image.Image) -> dict[str, float]:
    gray = img.convert("L")
    arr = np.asarray(gray).astype(np.float32) / 255.0
    # Use a simple edge estimate and brightness
    edges = gray.filter(ImageFilter.FIND_EDGES)
    earr = np.asarray(edges).astype(np.float32) / 255.0
    return {
        "aerial_mean_brightness": float(arr.mean()),
        "aerial_edge_strength": float(earr.mean()),
        "aerial_texture": float(arr.std()),
    }


def ingest(config: dict[str, Any], data_dir: str = "data/aerial") -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    p = pathlib.Path(data_dir)
    if not p.exists():
        return events
    for path in itertools.chain(p.glob("*.jpg"), p.glob("*.jpeg"), p.glob("*.png"), p.glob("*.ppm")):
        try:
            with Image.open(path) as img:
                feats = _image_features(img)
        except Exception:
            continue
        evt = {
            "id": gen_id("air"),
            "source": "aerial",
            "timestamp": now_iso(),
            "lat": None,
            "lon": None,
            "features": feats,
            "artifacts": {"image_path": str(path)},
        }
        events.append(evt)
    return events

