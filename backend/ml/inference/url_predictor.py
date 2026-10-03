"""URL inference: features -> model -> probability -> explanation. The URL is never requested."""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Dict

import joblib
import numpy as np

from ml.explainability.url_explainer import explain_url
from ml.inference.predictor import ModelNotLoadedError, risk_level
from ml.preprocessing.url import FEATURE_NAMES, FEATURE_VERSION, feature_vector

class UrlPredictor:
    def __init__(self, model_dir: str | Path = "models/url"):
        self.model_dir = Path(model_dir)
        self._lock = threading.Lock()
        self._loaded = False
        self.model = None
        self.stats = None
        self.metadata: Dict = {}

    def load(self) -> None:
        with self._lock:
            if self._loaded:
                return
            model_path = self.model_dir / "model.pkl"
            if not model_path.exists():
                raise ModelNotLoadedError(
                    f"Model files not found in '{self.model_dir}'. Run `python train_url.py --data <url_dataset.csv>` first."
                )
            self.model = joblib.load(model_path)
            stats_path = self.model_dir / "feature_stats.pkl"
            self.stats = joblib.load(stats_path) if stats_path.exists() else None
            meta_path = self.model_dir / "metadata.json"
            self.metadata = json.loads(meta_path.read_text()) if meta_path.exists() else {}
            if list(getattr(self.model, "classes_", [0, 1])) != [0, 1]:
                raise ModelNotLoadedError("The URL model has an unexpected class order; column 1 of predict_proba must be label 1 (malicious). Retrain it.")
            if self.metadata.get("feature_version") != FEATURE_VERSION:
                raise ModelNotLoadedError(
                    f"The URL model was trained with feature version {self.metadata.get('feature_version', 'unknown (pre-versioning)')}, "
                    f"but this code uses version {FEATURE_VERSION}. Retrain with `python train_url.py --data <url_dataset.csv>`."
                )
            trained_features = self.metadata.get("feature_names")
            if trained_features and trained_features != FEATURE_NAMES:
                raise ModelNotLoadedError("The URL model was trained with a different feature set. Retrain with `python train_url.py`.")
            self._loaded = True

    @property
    def model_name(self) -> str:
        return self.metadata.get("best_model", type(self.model).__name__)

    def predict(self, url: str) -> Dict:
        self.load()
        vector = np.asarray(feature_vector(url), dtype=np.float64)
        probability = float(self.model.predict_proba(vector.reshape(1, -1))[0][1])
        prediction = "phishing" if probability >= 0.5 else "safe"
        risk_score = round(probability * 100, 2)
        return {
            "prediction": prediction,
            "probability": round(probability, 4),
            "risk_score": risk_score,
            "confidence_score": round(max(probability, 1 - probability) * 100, 2),
            "risk_level": risk_level(risk_score),
            "explanation": explain_url(prediction, probability, url, self.model, vector, self.stats),
            "model": self.model_name,
        }
