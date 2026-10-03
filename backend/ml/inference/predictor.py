"""Inference: preprocessing -> TF-IDF -> model -> probability -> explanation."""
from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Dict

import joblib

from ml.explainability import explain
from ml.preprocessing import preprocess_email


class ModelNotLoadedError(RuntimeError):
    pass


def risk_level(score: float) -> str:
    if score < 30:
        return "low"
    if score < 60:
        return "medium"
    if score < 80:
        return "high"
    return "critical"


class PhishingPredictor:
    train_hint = "python train.py --data <dataset.csv>"

    def __init__(self, model_dir: str | Path = "models"):
        self.model_dir = Path(model_dir)
        self._lock = threading.Lock()
        self._loaded = False
        self.model = None
        self.tfidf = None
        self.term_direction = None
        self.metadata: Dict = {}

    def load(self) -> None:
        with self._lock:
            if self._loaded:
                return
            model_path = self.model_dir / "model.pkl"
            tfidf_path = self.model_dir / "tfidf.pkl"
            if not model_path.exists() or not tfidf_path.exists():
                raise ModelNotLoadedError(
                    f"Model files not found in '{self.model_dir}'. Run `{self.train_hint}` first."
                )
            self.model = joblib.load(model_path)
            self.tfidf = joblib.load(tfidf_path)
            direction_path = self.model_dir / "term_direction.pkl"
            self.term_direction = joblib.load(direction_path) if direction_path.exists() else None
            meta_path = self.model_dir / "metadata.json"
            self.metadata = json.loads(meta_path.read_text()) if meta_path.exists() else {}
            self._loaded = True

    @property
    def model_name(self) -> str:
        return self.metadata.get("best_model", type(self.model).__name__)

    def predict(self, subject: str, sender: str, body: str) -> Dict:
        self.load()
        cleaned = preprocess_email(subject, body)
        x = self.tfidf.transform([cleaned])
        probability = float(self.model.predict_proba(x)[0][1])
        prediction = "phishing" if probability >= 0.5 else "safe"
        risk_score = round(probability * 100, 2)
        confidence = round(max(probability, 1 - probability) * 100, 2)
        explanation = explain(prediction, probability, subject, sender, body, self.model, self.tfidf, x, self.term_direction)
        return {
            "prediction": prediction,
            "probability": round(probability, 4),
            "risk_score": risk_score,
            "confidence_score": confidence,
            "risk_level": risk_level(risk_score),
            "explanation": explanation,
            "model": self.model_name,
        }
