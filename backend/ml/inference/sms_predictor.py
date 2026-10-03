"""SMS inference: preprocessing -> TF-IDF -> model -> probability -> explanation."""
from __future__ import annotations

from typing import Dict

from ml.explainability.sms_explainer import explain_sms
from ml.inference.predictor import PhishingPredictor, risk_level
from ml.preprocessing.sms import preprocess_sms


class SmsPredictor(PhishingPredictor):
    """Loads model.pkl / tfidf.pkl / term_direction.pkl from the SMS model folder (same artefact layout as email)."""

    train_hint = "python train_sms.py --data <sms_dataset.csv>"

    def predict(self, message: str, sender: str = "") -> Dict:  # type: ignore[override]
        self.load()
        x = self.tfidf.transform([preprocess_sms(message)])
        probability = float(self.model.predict_proba(x)[0][1])
        prediction = "phishing" if probability >= 0.5 else "safe"
        risk_score = round(probability * 100, 2)
        return {
            "prediction": prediction,
            "probability": round(probability, 4),
            "risk_score": risk_score,
            "confidence_score": round(max(probability, 1 - probability) * 100, 2),
            "risk_level": risk_level(risk_score),
            "explanation": explain_sms(prediction, probability, message, sender, self.model, self.tfidf, x, self.term_direction),
            "model": self.model_name,
        }
