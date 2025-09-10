from __future__ import annotations

import pathlib
import warnings
from collections.abc import Iterable

import joblib
import numpy as np
from sklearn.exceptions import InconsistentVersionWarning
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline


class SocialNLP:
    def __init__(self, model_dir: str = "artifacts/models") -> None:
        self.model_dir = pathlib.Path(model_dir)
        self.model_path = self.model_dir / "social_nlp.joblib"
        self.pipeline: Pipeline | None = None
        self._ensure_model()

    def _ensure_model(self) -> None:
        if self.model_path.exists():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", InconsistentVersionWarning)
                try:
                    self.pipeline = joblib.load(self.model_path)
                    return
                except Exception:
                    # Fallback to (re)train if load fails
                    pass
        self.model_dir.mkdir(parents=True, exist_ok=True)
        texts, labels = self._load_training_data()
        self.pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
                ("clf", SGDClassifier(loss="log_loss", max_iter=1000, tol=1e-3, random_state=42)),
            ]
        )
        self.pipeline.fit(texts, labels)
        joblib.dump(self.pipeline, self.model_path)

    def _load_training_data(self) -> tuple[list[str], list[int]]:
        path = pathlib.Path("data/social/training_social.csv")
        texts: list[str] = []
        labels: list[int] = []  # 1=threat-indicative, 0=benign
        if path.exists():
            import csv

            with path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    t = (r.get("text") or "").strip()
                    y = int(r.get("label") or 0)
                    if t:
                        texts.append(t)
                        labels.append(1 if y else 0)
        if not texts:
            # Minimal inline seed dataset
            seed: list[tuple[str, int]] = [
                ("Illegal dumping spotted near river", 1),
                ("Unauthorized excavation within protected forest", 1),
                ("Pipeline tampering reported by locals", 1),
                ("Great weather for a hike today", 0),
                ("Birds nesting by the lake, beautiful scene", 0),
                ("Road repair completed successfully", 0),
            ]
            texts = [s for s, _ in seed]
            labels = [y for _, y in seed]
        return texts, labels

    def threat_score(self, texts: Iterable[str]) -> float:
        if self.pipeline is None:
            self._ensure_model()
        X = list(texts)
        if not X:
            return 0.0
        proba = self.pipeline.predict_proba(X)[:, 1]
        return float(np.clip(proba.mean(), 0.0, 1.0))

    def update_with_feedback(self, texts: Iterable[str], label: int) -> None:
        # Optional: online learning via partial_fit when available
        # For simplicity, refit with small batch including the new data
        if self.pipeline is None:
            self._ensure_model()
        base_texts, base_labels = self._load_training_data()
        X = base_texts + list(texts)
        y = base_labels + [label] * len(list(texts))
        self.pipeline.fit(X, y)
        joblib.dump(self.pipeline, self.model_path)
